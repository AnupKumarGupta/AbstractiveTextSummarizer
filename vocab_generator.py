import os
from nltk.tokenize import TweetTokenizer
import xml.etree.ElementTree as ET
from collections import Counter

tokenizer = TweetTokenizer()
token_count_list = {}


def get_files():
    file_list = []
    for root, dirs, files in os.walk("data/article", topdown=False):
        for name in files:
            file_location = os.path.join(root, name)
            file_list.append(file_location)
    return file_list


def get_text_from_files(file_list):
    text_data = ""
    for file_ in file_list:
        file_r = open(file_, 'r')
        tree = ET.parse(file_r)
        root = tree.getroot()
        text_data += root[3].text
    return text_data


def tokenize_data(text_data):
    token_list = tokenizer.tokenize(text_data)
    return Counter(token_list)


def sort_token_list(vocab_dict):
    var = sorted(vocab_dict.iteritems(), key=lambda (k, v): (v, k))
    return var


def gen_vocab_file(sorted_vocab_dict):
    file_w = open("data/vocab", 'w')
    i = 0
    for key, value in sorted_vocab_dict:
        if not key.isnumeric():
            file_w.write(str(key) + " " + str(value)+'\n')


def voccab_generator():
    print "Collecting files"
    file_list = get_files()
    print "Files collected"
    text = get_text_from_files(file_list)
    print "Text from files collected"
    vocab_dict = tokenize_data(text)
    print "Text from files tokenized"
    sorted_vocab_dict = sort_token_list(vocab_dict)
    print "Tokenized pairs sorted basis of count"
    gen_vocab_file(sorted_vocab_dict)
    print "Voccab file generated"

voccab_generator()