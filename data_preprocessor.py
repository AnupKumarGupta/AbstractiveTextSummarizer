import os, glob
import xml.etree.ElementTree as ET

article_file_list = []
abstract_files_list = []

"""Collect articles"""
def get_articles():
    for root, dirs, files in os.walk("duc2004/article", topdown=False):
        for name in files:
            file_location = os.path.join(root, name)
            article_file_list.append(file_location)
    return article_file_list

"""collect corresponding abstracts"""
def get_abstracts():
    for files in article_file_list:
        file_ = open(files, 'r')
        print "parsing: ",file_
        tree = ET.parse(file_)
        root = tree.getroot()
        text_id = root[0].text
        article = root[3].text
        abstract_files_list.append(glob.glob1("duc2004/abstract/", '*'+text_id.strip()+'*'))
    return abstract_files_list

get_articles()
print get_abstracts()
