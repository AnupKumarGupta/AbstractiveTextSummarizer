import Queue
import time
from collections import namedtuple
from random import shuffle
from threading import Thread

import numpy as np
import tensorflow as tf

import data

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
        """
            Fill input queue with ModelInput.

        """
        start_id = self._vocab.WordToId(data.SENTENCE_START)
        end_id = self._vocab.WordToId(data.SENTENCE_END)
        pad_id = self._vocab.WordToId(data.PAD_TOKEN)
        input_gen = self._text_generator(data.example_gen(self._data_path))
        while True:
            (article, abstract) = input_gen.next()
            article_sentences = [sent.strip() for sent in data.paragraph_to_sentences(article, include_token=False)]
            abstract_sentences = [sent.strip() for sent in data.paragraph_to_sentences(abstract, include_token=False)]

            enc_inputs = []
            dec_inputs = [start_id]

            # Convert first N sentences to word IDs, stripping existing <s> and </s>.
            for i in xrange(min(self._max_article_sentences, len(article_sentences))):
                enc_inputs += data.get_ids_from_words(article_sentences[i], self._vocab)

            for i in xrange(min(self._max_abstract_sentences, len(abstract_sentences))):
                dec_inputs += data.get_ids_from_words(abstract_sentences[i], self._vocab)

            # Filter out too-short input
            if len(enc_inputs) < self._hps.min_input_len or len(dec_inputs) < self._hps.min_input_len:
                tf.logging.warning('Drop an example - too short.\nenc:%d\ndec:%d', len(enc_inputs), len(dec_inputs))
                continue

            # If we're not truncating input, throw out too-long input
            if not self._truncate_input:
                if len(enc_inputs) > self._hps.enc_timesteps or len(dec_inputs) > self._hps.dec_timesteps:
                    tf.logging.warning('Drop an example - too long.\nenc:%d\ndec:%d', len(enc_inputs), len(dec_inputs))
                    continue

            # If we are truncating input, do so if necessary
            else:
                if len(enc_inputs) > self._hps.enc_timesteps:
                    enc_inputs = enc_inputs[:self._hps.enc_timesteps]
                if len(dec_inputs) > self._hps.dec_timesteps:
                    dec_inputs = dec_inputs[:self._hps.dec_timesteps]

            # targets is dec_inputs without <s> at beginning, plus </s> at end
            targets = dec_inputs[1:]
            targets.append(end_id)

            # Now len(enc_inputs) should be <= enc_timesteps, and
            # len(targets) = len(dec_inputs) should be <= dec_timesteps

            enc_input_len = len(enc_inputs)
            dec_output_len = len(targets)

            # Pad if necessary
            while len(enc_inputs) < self._hps.enc_timesteps:
                enc_inputs.append(pad_id)
            while len(dec_inputs) < self._hps.dec_timesteps:
                dec_inputs.append(end_id)
            while len(targets) < self._hps.dec_timesteps:
                targets.append(end_id)

            element = ModelInput(enc_inputs, dec_inputs, targets, enc_input_len, dec_output_len,
                                 ' '.join(article_sentences), ' '.join(abstract_sentences))
            self._input_queue.put(element)

    def _fill_bucket_input_queue(self):
        """
        Fill bucketed batches into the bucket_input_queue.
        """
        while True:
            inputs = []

            for _ in xrange(self._hps.batch_size * BUCKET_CACHE_BATCH):
                inputs.append(self._input_queue.get())

            if self._bucketing:
                inputs = sorted(inputs, key=lambda inp: inp.enc_len)

            batches = []
            for i in xrange(0, len(inputs), self._hps.batch_size):
                batches.append(inputs[i:i + self._hps.batch_size])

            shuffle(batches)
            for b in batches:
                self._bucket_input_queue.put(b)

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

    def _text_generator(self, example_gen):
        """
        Generates article and abstract text from tf.Example. Raises ValueError

        Information: Retrieve the next item from the iterator by calling its next() method.
                     If default is given, it is returned if the iterator is exhausted,
                     otherwise StopIteration is raised.

                     https://docs.python.org/2/library/functions.html#next

        """
        while True:
            e = example_gen.next()
            try:
                article_text = self._get_example_feature_text(e, self._article_key)
                abstract_text = self._get_example_feature_text(e, self._abstract_key)

            except ValueError:
                tf.logging.error('Failed to get article or abstract from example')
                continue

            yield (article_text, abstract_text)

    def _get_example_feature_text(self, example, key):
        """Extract text for a feature from td.Example.

        Args:
          ex: tf.Example.
          key: key of the feature to be extracted.
        Returns:
          feature: a feature text extracted.
        """
        return example.features.feature[key].bytes_list.value[0]
