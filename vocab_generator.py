import os
from nltk.tokenize import TweetTokenizer
import xml.etree.ElementTree as ET
from collections import Counter

tokenizer = TweetTokenizer()
token_count_list = {}


def get_files():
    file_list = []
    for root, dirs, files in os.walk("data/tagged_data", topdown=False):
        for name in files:
            file_location = os.path.join(root, name)
            file_list.append(file_location)
    return file_list


def get_text_from_files(file_list):
    text_data = ""
    for file_ in file_list:
        file_r = open(file_, 'r')
        article = file_r.read().split('\t')[0].replace("article=", "")
        text_data += article
    return text_data


def tokenize_data(text_data):
    token_list = tokenizer.tokenize(text_data)
    token_list.extend(['<UNK>', '<PAD>'])
    # Adding Special Tokens { <UNK> :"UNKNOWN_TOKEN", <PAD> : "PAD_TOKEN"} to vocab
    return Counter(token_list)


def sort_token_list(vocab_dict):
    var = sorted(vocab_dict.iteritems(), key=lambda (k, v): (v, k))
    return var


def parse_numbers_with_char(str_data):
    replace_dict = \
        {
            ".": "",
            ",": "",
            "-": "",
            "/": "",
            ":": "",
            "(": "",
            ")": "",
            "st": "",
            "nd": "",
            "rd": "",
            "th": "",
            "s": "",
            "  ": ""  # For annoying "(800)  281-1184"
        }
    for key, value in replace_dict.iteritems():
        str_data = str_data.replace(key, value)
    return str_data


def is_numeric(str_data):
    parsed_data = parse_numbers_with_char(str_data)
    if parsed_data.strip() == '' or parsed_data.isdigit():  #isnumeric() replaced by isdigit()
        return True
    else:
        return False


def gen_vocab_file(sorted_vocab_dict):
    file_w = open("data/vocab", 'w')
    print "File Opened"
    i = 0
    for key, value in sorted_vocab_dict:
        if not is_numeric(key):
            file_w.write(str(key) + " " + str(value) + '\n')
    file_w.close()
    print "File Closed"


def vocab_generator():
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
    print "Vocab file generated"


vocab_generator()
