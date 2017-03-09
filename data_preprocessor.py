import os, glob
import xml.etree.ElementTree as ET
import unescape_html
import tag_input

article_file_list = []
abstract_files_list = []
tag_input_data = tag_input.tag_data()

"""Collect articles"""


def get_articles():
    for root, dirs, files in os.walk("duc2004/article", topdown=False):
        for name in files:
            file_location = os.path.join(root, name)
            article_file_list.append(file_location)
    return article_file_list


def clean_text():
    for files in article_file_list:
        file_r = open(files, 'r')
        text_data = file_r.read()
        clean_text_data = unescape_html.unescape(text_data)
        file_r.close()
        file_w = open(files, 'w')
        file_w.write(clean_text_data)
        file_w.close()

    """collect corresponding abstracts"""


def get_abstracts():
    for files in article_file_list:
        abstract_file_list_per_article = ['ruk be']
        file_ = open(files, 'r')
        print "parsing: ", file_
        tree = ET.parse(file_)
        root = tree.getroot()
        text_id = root[0].text
        article = root[3].text
        #
        #
        # Changes to be made
        #
        #
        abstract_file_list_per_article = (glob.glob1("duc2004/abstract/", '*' + text_id.strip() + '*'))
        prepare_data_for_training(article, abstract_file_list_per_article)
    return abstract_files_list


def prepare_data_for_training(article_data, abstract_file_list_per_article):
    for abstract_file in abstract_file_list_per_article:
        file_abstract_r = open("duc2004/abstract/"+abstract_file, 'r')
        abstract_data = file_abstract_r.read().strip()
        training_data = tag_input_data.tag_document(article_data, abstract_data)
        print "hi"
        # file_abstract_r.close()
        print training_data


get_articles()
clean_text()
print get_abstracts()

# print unescape_html.__dict_replace("Unescapes :: Hello I am new. I cant unescape &amp;",{"Hello":"Hi","new":"changed"})
# print unescape_html.unescape("Unescapes :: Hello I am new. I escape chars &AMP; &amp;",{"Hello":"Hi","new":"changed"})
