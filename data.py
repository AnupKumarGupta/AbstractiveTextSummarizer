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

    def CheckVocab(self, word):
        if word not in self._word_to_id:
            return None
        return self._word_to_id[word]

    def WordToId(self, word):
        if word not in self._word_to_id:
            return self._word_to_id[UNKNOWN_TOKEN]
        return self._word_to_id[word]

    def IdToWord(self, word_id):
        if word_id not in self._id_to_word:
            raise ValueError('Id not found in vocab: %d.' % word_id)
        return self._id_to_word[word_id]

    def NumIds(self): 
        return self._count