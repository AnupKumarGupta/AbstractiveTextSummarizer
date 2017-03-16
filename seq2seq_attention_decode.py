"""Module for decoding."""

import os
import time
import data
import beam_search
import tensorflow as tf

FLAGS = tf.app.flags.FLAGS
tf.app.flags.DEFINE_integer('max_decode_steps', 1000000,
                            'Number of decoding steps.')

tf.app.flags.DEFINE_integer('decode_batches_per_ckpt', 8000,
                            'Number of batches to decode before restoring next checkpoint')

DECODE_LOOP_DELAY_SECS = 60
DECODE_IO_FLUSH_INTERVAL = 100


class DecodeIO(object):
    def __init__(self, outdir):
        self._cnt = 0
        self._outputdir = outdir
        if not os.path.exists(self._outputdir):
            os.mkdir(self._outputdir)
        self._ref_file = None
        self._decode_file = None

    def write(self, reference, decode):
        """
            Args:
              reference: The human (correct) result.
              decode: The machine-generated result
        """
        self._ref_file.write('output=%s\n' % reference)
        self._decode_file.write('output=%s\n' % decode)
        self._cnt += 1

        if self._cnt % DECODE_IO_FLUSH_INTERVAL == 0:
            self._ref_file.flush()
            self._decode_file.flush()
        exit(0)

    def reset_files(self):
        """
            Resets the output files. Must be called once before write().
        """
        if self._ref_file: self._ref_file.close()
        if self._decode_file: self._decode_file.close()

        timestamp = int(time.time())
        self._ref_file = open(os.path.join(self._outputdir, 'ref%d' % timestamp), 'w')
        self._decode_file = open(os.path.join(self._outputdir, 'decode%d' % timestamp), 'w')


class BSDecoder(object):
    """Beam search decoder."""

    def __init__(self, model, batch_reader, hps, vocab):

        """Beam search decoding.

        Args:
          model: The seq2seq attentional model.
          batch_reader: The batch data reader.
          hps: Hyperparamters.
          vocab: Vocabulary
        """
        self._model = model
        self._model.build_graph()
        self._batch_reader = batch_reader
        self._hps = hps
        self._vocab = vocab
        self._saver = tf.train.Saver()
        self._decode_io = DecodeIO(FLAGS.decode_dir)

    def _decode(self, saver, sess):
        """Restore a checkpoint and decode it.

        Args:
            saver: Tensorflow checkpoint saver.
            sess: Tensorflow session.

        Returns:
            If success, returns true, otherwise, false.

        Information:
            If we want TensorFlow to automatically choose an existing and supported device to run
            the operations in case the specified one doesn't exist, we can set
            allow_soft_placement to True in the configuration option when creating the session.

        """
        ckpt_state = tf.train.get_checkpoint_state(FLAGS.log_root)
        if not (ckpt_state and ckpt_state.model_checkpoint_path):
            tf.logging.info('No model to decode yet at %s', FLAGS.log_root)
            return False

        tf.logging.info('checkpoint path %s', ckpt_state.model_checkpoint_path)
        ckpt_path = os.path.join(FLAGS.log_root, os.path.basename(ckpt_state.model_checkpoint_path))

        tf.logging.info('renamed checkpoint path %s', ckpt_path)
        saver.restore(sess, ckpt_path)

        self._decode_io.reset_files()
        for _ in xrange(FLAGS.decode_batches_per_ckpt):
            (article_batch, _, _, article_lens, _, _, origin_articles,
             origin_abstracts) = self._batch_reader.next_batch()
            for i in xrange(self._hps.batch_size):
                bs = beam_search.BeamSearch(
                    self._model, self._hps.batch_size,
                    self._vocab.WordToId(data.SENTENCE_START),
                    self._vocab.WordToId(data.SENTENCE_END),
                    self._hps.dec_timesteps)

                article_batch_cp = article_batch.copy()
                article_batch_cp[:] = article_batch[i:i + 1]
                article_lens_cp = article_lens.copy()
                article_lens_cp[:] = article_lens[i:i + 1]
                best_beam = bs.BeamSearch(sess, article_batch_cp, article_lens_cp)[0]
                decode_output = [int(t) for t in best_beam.tokens[1:]]
                self._decode_batch(origin_articles[i], origin_abstracts[i], decode_output)
        return True

    def decode_loop(self):
        """
            Decoding loop for long running process.
        """
        sess = tf.Session(config=tf.ConfigProto(allow_soft_placement=True))
        step = 0
        while step < FLAGS.max_decode_steps:
            time.sleep(DECODE_LOOP_DELAY_SECS)
            if not self._decode(self._saver, sess):
                continue
            step += 1

    def _decode_batch(self, article, abstract, output_ids):
        """
        Convert id to words and writing results.

        Args:
          article: The original article string.
          abstract: The human (correct) abstract string.
          output_ids: The abstract word ids output by machine.

        """
        decoded_output = ' '.join(data.get_words_from_ids(output_ids, self._vocab))
        end_p = decoded_output.find(data.SENTENCE_END, 0)
        if end_p != -1:
            decoded_output = decoded_output[:end_p]
        tf.logging.info('article:  %s', article)
        tf.logging.info('abstract: %s', abstract)
        tf.logging.info('decoded:  %s', decoded_output)
        self._decode_io.write(abstract, decoded_output.strip())
