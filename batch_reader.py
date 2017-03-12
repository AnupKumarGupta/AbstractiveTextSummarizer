import Queue
from collections import namedtuple
from threading import Thread

ModelInput = namedtuple('ModelInput', 'enc_input, dec_input, target, enc_len, dec_len, origin_article,origin_abstract')

BUCKET_CACHE_BATCH = 100
QUEUE_NUM_BATCH = 100


class Batcher(object):
    """Batch reader with shuffling and bucketing support."""

    def __init__(self, data_path, vocab, hps, article_key, abstract_key, max_article_sentences,
                 max_abstract_sentences, bucketing=True, truncate_input=False):

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
          truncate_input: Whether to truncate input that is too long. Alternative is
            to discard such examples.
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
        self._bucket_input_queue = Queue.Queue(QUEUE_NUM_BATCH)
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

    def _fill_input_queue(self):
        pass

    def _fill_bucket_input_queue(self):
        pass

    def _watch_threads(self):
        pass
