# SPECIAL TOKENS
#
# Usage
# =====
# Used to identify start and end of documents, paragraphs and sentences
#

import sys

PARAGRAPH_START = '<p>'
PARAGRAPH_END = '</p>'
SENTENCE_START = '<s>'
SENTENCE_END = '</s>'
UNKNOWN_TOKEN = '<UNK>'
PAD_TOKEN = '<PAD>'
DOCUMENT_START = '<d>'
DOCUMENT_END = '</d>'


class Vocab(object):
    """Vocabulary class for mapping words and ids."""

    def __init__(self, vocab_file="/home/textsum/Documents/AbstractiveTextSummarizer/data/vocab", max_size=20000):
        self._word_to_id = {}
        self._id_to_word = {}
        self._count = 0

        with open(vocab_file, 'r') as vocab_r:
            for line in vocab_r:
                pieces = line.split()

                if len(pieces) != 2:
                    sys.stderr.write('Bad line: %s\n' % line)
                    continue

                if pieces[0] in self._word_to_id:
                    raise ValueError('Duplicated word: %s.' % pieces[0])

                self._word_to_id[pieces[0]] = self._count
                self._id_to_word[self._count] = pieces[0]
                self._count += 1

                if self._count > max_size:
                    raise ValueError('Too many words: >%d.' % max_size)

    def check_vocab(self, word):
        if word not in self._word_to_id:
            return None
        return self._word_to_id[word]

    def word_to_id(self, word):
        if word not in self._word_to_id:
            return self._word_to_id[UNKNOWN_TOKEN]
        return self._word_to_id[word]

    def id_to_word(self, word_id):
        if word_id not in self._id_to_word:
            raise ValueError('Id not found in vocab: %d.' % word_id)
        return self._id_to_word[word_id]

    def count_of_ids(self):
        return self._count


def pad(ids, pad_id, length):
    """pad or trim list to len length.

    Args:
      ids: list of ints to pad
      pad_id: what to pad with
      length: length to pad or trim to

    Returns:
      ids trimmed or padded with pad_id
    """
    assert pad_id is not None
    assert length is not None

    if len(ids) < length:
        a = [pad_id] * (length - len(ids))
        return ids + a
    else:
        return ids[:length]


def get_ids_from_words(text, vocab, pad_len=None, pad_id=None):
    """Get ids corresponding to words in text.

    Assumes tokens separated by space.

    Args:
      text: a string
      vocab: TextVocabularyFile object
      pad_len: int, length to pad to
      pad_id: int, word id for pad symbol

    Returns:
      A list of ints representing word ids.
    """
    ids = []
    for w in text.split():
        i = vocab.word_to_id(w)
        if i >= 0:
            ids.append(i)
        else:
            ids.append(vocab.word_to_id(UNKNOWN_TOKEN))
    if pad_len is not None:
        return pad(ids, pad_id, pad_len)
    return ids


def get_words_from_ids(ids_list, vocab):
    """Get words from ids.

    Args:
      ids_list: list of int32
      vocab: TextVocabulary object

    Returns:
      List of words corresponding to ids.
    """
    assert isinstance(ids_list, list), '%s  is not a list' % ids_list
    return [vocab.id_to_word(i) for i in ids_list]
