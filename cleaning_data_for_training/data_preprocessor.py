import glob
import os
import xml.etree.ElementTree as ET
import tag_input
import data_cleaner

article_file_list = []
tag_input_data = tag_input.tag_data()

"""Collect articles"""


def get_articles():
    for root, dirs, files in os.walk("../data/article", topdown=False):
        for name in files:
            file_location = os.path.join(root, name)
            article_file_list.append(file_location)

def clean_text():
    for files in article_file_list:
        file_r = open(files, 'r')
        text_data = file_r.read()
        clean_text_data = data_cleaner.unescape(text_data, {"``": "", "''": ""})
        clean_text_data = data_cleaner.remove_fake_newlines(clean_text_data)
        file_r.close()
        file_w = open(files, 'w')
        file_w.write(clean_text_data)
        file_w.close()


def write_tarining_data_to_file(article_data, abstract_file_list_per_article):
    for abstract_file in abstract_file_list_per_article:
        file_abstract_r = open("../data/abstract/" + abstract_file, 'r')
        abstract_data = file_abstract_r.read().strip()+"."
        training_data = tag_input_data.tag_document(article_data, abstract_data)
        file_w = open("../data/clean_data/" + file_abstract_r.name.split('/')[-1], 'w')
        file_w.write(training_data)


def preprocess_training_data(is_clean):
    get_articles()

    if is_clean == False:
        clean_text()

    for files in article_file_list:
        file_ = open(files, 'r')
        print "parsing: ", file_
        tree = ET.parse(file_)
        root = tree.getroot()
        text_id = root[0].text
        article = root[3].text
        abstract_file_list_per_article = (glob.glob1("../data/abstract/", '*' + text_id.strip() + '*'))
        write_tarining_data_to_file(article, abstract_file_list_per_article)


preprocess_training_data(False)