"""Module for decoding."""

import os
import time

import tensorflow as tf

FLAGS = tf.app.flags.FLAGS
tf.app.flags.DEFINE_integer('max_decode_steps', 1000000,
                            'Number of decoding steps.')

tf.app.flags.DEFINE_integer('decode_batches_per_ckpt', 8000,
                            'Number of batches to decode before restoring next '
                            'checkpoint')

DECODE_LOOP_DELAY_SECS = 60
DECODE_IO_FLUSH_INTERVAL = 100


class DecodeIO(object):
    def __init__(self, outdir):
        self._cnt = 0
        self._outdir = outdir
        if not os.path.exists(self._outdir):
            os.mkdir(self._outdir)
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
        self._ref_file = open(os.path.join(self._outdir, 'ref%d' % timestamp), 'w')
        self._decode_file = open(os.path.join(self._outdir, 'decode%d' % timestamp), 'w')
