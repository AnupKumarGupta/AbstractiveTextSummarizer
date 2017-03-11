"""

Usage
=====
Converts data from binary format to text format and vice-versa

Examples
========
python data_convert_example.py --command binary_to_text --in_file data/data --out_file data/text_data
python data_convert_example.py --command text_to_binary --in_file data/text_data --out_file data/binary_data

"""

import struct
import sys
import tensorflow as tf
from tensorflow.core.example import example_pb2

"""

Flags
=====
The 'tf.app.flags' module is presently a thin wrapper around argparse,
which implements a subset of the functionality in python-gflags. It is used
to parse the command line arguments.

"""

FLAGS = tf.app.flags.FLAGS
tf.app.flags.DEFINE_string('command', 'binary_to_text',
                           'Either binary_to_text or text_to_binary.'
                           'Specify FLAGS.in_file accordingly.')

tf.app.flags.DEFINE_string('in_file', '', 'path to file')
tf.app.flags.DEFINE_string('out_file', '', 'path to file')

"""

Usage
=====
Converts data from binary format to text format

Parameters
==========
No Parameters (Parameters are initialized by FLAGS via command line)

Example
=======

>>>python data_convert_example.py 
	--command binary_to_text 
	--in_file data.bin
	--out_file text_data.txt

"""


def _binary_to_text():
    # open the input file in read-binary mode
    reader = open(FLAGS.in_file, 'rb')

    # open the input file as write
    writer = open(FLAGS.out_file, 'w')

    while True:
        len_bytes = reader.read(8)
        if not len_bytes:
            sys.stderr.write('File reading completed\n')
            return

        # The result of 'struct.unpack' is a tuple, hence [0] is used
        str_len = struct.unpack('q', len_bytes)[0]
        tf_example_str = struct.unpack('%ds' % str_len, reader.read(str_len))[0]
        tf_example = example_pb2.Example.FromString(tf_example_str)
        examples = []
        for key in tf_example.features.feature:
            examples.append('%s=%s' % (key, tf_example.features.feature[key].bytes_list.value[0]))
        writer.write('%s\n' % '\t'.join(examples))
    reader.close()
    writer.close()


"""
Usage
=====
Converts data from text format to binary format

Parameters
==========
No Parameters (Parameters are initialized by FLAGS via command line)

Example
=======
>>>python data_convert_example.py 
	--command text_to_binary 
	--in_file text_data.txt
	--out_file data.bin
"""


def _text_to_binary():
    # open the input file in read mode
    inputs = open(FLAGS.in_file, 'r').readlines()

    # open the input file in write-binary mode
    writer = open(FLAGS.out_file, 'wb')
    for inp in inputs:
        tf_example = example_pb2.Example()

        # 'article' and 'abstract' are separated by <tab>
        for feature in inp.strip().split('\t'):
            (k, v) = feature.split('=')
            tf_example.features.feature[k].bytes_list.value.extend([v])

        tf_example_str = tf_example.SerializeToString()
        str_len = len(tf_example_str)
        writer.write(struct.pack('q', str_len))
        writer.write(struct.pack('%ds' % str_len, tf_example_str))
    writer.close()


def main(unused_argv):
    assert FLAGS.command and FLAGS.in_file and FLAGS.out_file
    if FLAGS.command == 'binary_to_text':
        _binary_to_text()
    elif FLAGS.command == 'text_to_binary':
        _text_to_binary()


if __name__ == '__main__':
    tf.app.run()
