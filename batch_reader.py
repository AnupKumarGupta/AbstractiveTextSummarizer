import Queue
import time
from collections import namedtuple
from threading import Thread

import numpy as np
import tensorflow as tf

ModelInput = namedtuple('ModelInput', 'enc_input, dec_input, target, enc_len, dec_len, origin_article,origin_abstract')

BUCKET_CACHE_BATCH = 100
QUEUE_NUM_BATCH = 100


class Batcher(object):
    def __init__(self, data_path, vocab, hps, article_key, abstract_key, max_article_sentences, max_abstract_sentences,
                 bucketing=True, truncate_input=False):

        """Batcher constructor.

        Args:
          data_path: tf.Example filepattern.
          vocab: Vocabulary.
          hps: Seq2SeqAttention model hyperparameters.
          article_key: article feature key in tf.Example.
          abstract_key: abstract feature key in tf.Example.
          max_article_sentences: Max number of sentences used from article.
          max_abstract_sentences: Max number of sentences used from abstract.
          bucketing: Whether bucket articles of similar length into the same batch.
          truncate_input: Whether to truncate input that is too long. Alternative is to discard such examples.

        Information:
           bucketing: https://www.tensorflow.org/tutorials/seq2seq#bucketing_and_padding

        """
        self._data_path = data_path
        self._vocab = vocab
        self._hps = hps
        self._article_key = article_key
        self._abstract_key = abstract_key
        self._max_article_sentences = max_article_sentences
        self._max_abstract_sentences = max_abstract_sentences
        self._bucketing = bucketing
        self._truncate_input = truncate_input

        self._input_queue = Queue.Queue(QUEUE_NUM_BATCH * self._hps.batch_size)
        self._bucket_input_queue = Queue.Queue(BUCKET_CACHE_BATCH)
        self._input_threads = []

        for _ in xrange(16):
            self._input_threads.append(Thread(target=self._fill_input_queue))
            self._input_threads[-1].daemon = True
            self._input_threads[-1].start()
        self._bucketing_threads = []

        for _ in xrange(4):
            self._bucketing_threads.append(Thread(target=self._fill_bucket_input_queue))
            self._bucketing_threads[-1].daemon = True
            self._bucketing_threads[-1].start()

        self._watch_thread = Thread(target=self._watch_threads)
        self._watch_thread.daemon = True
        self._watch_thread.start()

    """Batch reader with shuffling and bucketing support."""

    def next_batch(self):
        """Returns a batch of inputs for seq2seq attention model.

        Returns:
          enc_batch: A batch of encoder inputs [batch_size, hps.enc_timestamps].
          dec_batch: A batch of decoder inputs [batch_size, hps.dec_timestamps].
          target_batch: A batch of targets [batch_size, hps.dec_timestamps].
          enc_input_len: encoder input lengths of the batch.
          dec_input_len: decoder input lengths of the batch.
          loss_weights: weights for loss function, 1 if not padded, 0 if padded.
          origin_articles: original article words.
          origin_abstracts: original abstract words.
        """
        # region Initialization of vectors with zeros or 'None'

        enc_batch = np.zeros(self._hps.batch_size, self._hps.enc_timesteps, dtype=np.int32)
        enc_input_lens = np.zeros(self._hps.batch_size, dtype=np.int32)
        dec_batch = np.zeros(self._hps.batch_size, self._hps.dec_timesteps, dtype=np.int32)
        dec_output_lens = np.zeros(self._hps.batch_size, dtype=np.int32)
        target_batch = np.zeros(self._hps.batch_size, self._hps.dec_timesteps, dtype=np.int32)
        loss_weights = np.zeros(self._hps.batch_size, self._hps.dec_timesteps, dtype=np.float32)

        # y = ['None'] * 3
        # print y
        # ['None', 'None', 'None']

        origin_articles = ['None'] * self._hps.batch_size
        origin_abstracts = ['None'] * self._hps.batch_size
        # endregion

        buckets = self._bucket_input_queue.get()

        for i in xrange(self._hps.batch_size):

            (enc_inputs, dec_inputs, targets, enc_input_len, dec_output_len, article, abstract) = buckets[i]

            origin_articles[i] = article
            origin_abstracts[i] = abstract
            enc_input_lens[i] = enc_input_len
            dec_output_lens[i] = dec_output_len
            enc_batch[i, :] = enc_inputs[:]
            dec_batch[i, :] = dec_inputs[:]
            target_batch[i, :] = targets[:]

            for j in xrange(dec_output_len):
                loss_weights[i][j] = 1

        return (enc_batch, dec_batch, target_batch, enc_input_lens, dec_output_lens, loss_weights, origin_articles,
                origin_abstracts)

    def _fill_input_queue(self):
        pass

    def _fill_bucket_input_queue(self):
        pass

    def _watch_threads(self):

        """
            Watch the daemon input threads and restart if dead.
            Collect all the alive threads and assign them to self._input_threads and
            self._bucketing_threads

            Information: Without daemon threads, we have to keep track of the threads, and tell them to exit, before our
                         program can completely quit. By setting them as daemon threads, we can let them run and forget
                         about them, and when our program quits, any daemon threads are killed automatically.

                         bucketing_threads[-1].daemon = True

                         http://stackoverflow.com/questions/190010/daemon-threads-explanation

        """
        while True:
            time.sleep(60)
            input_threads = []

            for t in self._input_threads:
                if t.is_alive():
                    input_threads.append(t)
                else:
                    tf.logging.error('Input thread found dead.')
                    # creating a new thread is any thread is found dead
                    new_t = Thread(target=self._fill_input_queue)
                    input_threads.append(new_t)
                    input_threads[-1].daemon = True
                    input_threads[-1].start()

            self._input_threads = input_threads

            bucketing_threads = []

            for t in self._bucketing_threads:
                if t.is_alive():
                    bucketing_threads.append(t)
                else:
                    tf.logging.error('Bucketing thread found dead.')
                    new_t = Thread(target=self._fill_bucket_input_queue)
                    # creating a new thread is any thread is found dead
                    bucketing_threads.append(new_t)
                    bucketing_threads[-1].daemon = True
                    bucketing_threads[-1].start()

            self._bucketing_threads = bucketing_threads
