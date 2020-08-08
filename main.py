#!/usr/bin/env python3
# -*- coding: utf_8 -*-
#
"""
    Copyright    : 2020 August 3.
    Organization : VAU Soft Tech
    Project      : vauwmflab-la
    Script Name  : main.py
    License      : T.B.D.
    Author       : A. R. Bhatt
    Contacts     : ab@vausofttech.com
    Version      : 0.0.1
"""
"""
    All import statements
"""
import os
import requests as rq
from bs4 import BeautifulSoup as bs
from collections import Counter
import unicodedata
import sys
from itertools import count

count_gen = count(1)

"""
    For carrying out Language Analysis, we need only text, without any punctuation
    marks. The text we are targeting to process, has punctuation marks not only 
    limited to Gujarati Language but also from other languages. Manual inspection 
    revealed that there may be punctuation marks from English, Hindi and Sanskrit 
    Language as well. 
    Therefore, below a variable holding the list of all the punctuation marks in
    entire unicode set is created using dictionary comprehension. This variable is 
    used later on to remove the punctuation marks from the text.
"""
translation_table = {i: " " for i in range(sys.maxunicode)
                     if unicodedata.category(chr(i)).startswith('P')}

curr_folder = os.getcwd()
in_txt_dir = os.path.join(curr_folder, "in")
out_txt_dir = os.path.join(curr_folder, "out")
if not os.path.exists(in_txt_dir):
    os.makedirs(in_txt_dir)
if not os.path.exists(out_txt_dir):
    os.makedirs(out_txt_dir)

"""
    Following just accepts text as input and using String class's translate method
    remove all possible punctuation marks from the text. So that the text can be processed 
    without any issues.
"""


def remove_punctuation(text):
    return text.translate(translation_table)


"""
    We now (from 2020-08-06) moving towards a setup that uses a text file called 
    config.ini to load all the defaults. Earlier everything was hard-coded.
    
    This routine sets up a few public variables after loading them from config file.
"""

base_uri = ""
page_list_file_name = ""


def load_config_file():
    import configparser as cf

    global base_uri, page_list_file_name

    if not os.path.exists("config.ini"):
        config = cf.ConfigParser()
        config['DEFAULT'] = {}
        config['gu.wikisource.org'] = {}
        config['gu.wikisource.org']['base_uri'] = 'https://gu.wikisource.org/wiki/'
        with open("config.ini") as configfile:
            config.write(configfile)

    config = cf.ConfigParser()
    config.read('config.ini')
    base_uri = config['gu.wikisource.org']['base_uri']
    page_list_file_name = config['gu.wikisource.org']['page_list_file_name']
    # print(base_uri, page_list_file_name, config.sections())
    return


def wikisourec_page_uri_generator():
    # Load list of URIs to be processed from a text file
    with open(page_list_file_name) as furis:
        uri_list = furis.readlines()

    # Now for each URI that is not already DONE, yield that URI to processing function.
    for a_uri in uri_list:

        if ":" in a_uri:
            a_uri_part, is_it_done = a_uri.split(":")
            a_uri_part = a_uri_part.strip()
        else:
            is_it_done = ""
            a_uri_part = a_uri.strip()

        if is_it_done.strip().upper() == "DONE":
            continue

        if a_uri_part == "":
            continue

        yield next(count_gen), a_uri_part, base_uri + a_uri_part
        # yield next(count_gen), 'પલકારા/માસ્તર_સાહેબ', base_uri + 'પલકારા/માસ્તર_સાહેબ'
    return


def wikisource_get_page_text(pg):
    print("Connecting to WikiSource to get the text for {}.".format(pg))
    status = rq.get(pg)
    if status.status_code == 200:
        print("Connection Successful. Received the text.")
        pg_content = bs(status.text, 'html.parser')
        pgttl = pg_content.h1.text
        pgtxt = ""
        for i, j in enumerate(pg_content.find_all(class_="prp-pages-output")):
            pgtxt = j.text
            break
    else:
        pgttl, pgtxt = -1, ""

    return pgttl, pgtxt


def check_whether_text_from_the_page_is_already_downloaded(in_fl_nm):
    return os.path.exists(in_fl_nm)


def get_text_from_the_local_file(full_file_name):
    print("Local copy found. So using that copy.")
    with open(full_file_name) as f:
        text = f.read()
    return text


def main():
    load_config_file()
    for a_number, page_name, page_uri in wikisourec_page_uri_generator():
        os_friendly_page_name = page_name.translate({ord("/"): "_"})
        print("Processing started for {} - {}".format(a_number, page_name))

        full_in_file_name = os.path.join(in_txt_dir, "{}-in.txt".format(os_friendly_page_name))
        full_ou_file_name = os.path.join(out_txt_dir, "{}-out.txt".format(os_friendly_page_name))
        if check_whether_text_from_the_page_is_already_downloaded(full_in_file_name):
            page_title = page_name
            page_content = get_text_from_the_local_file(full_in_file_name)
        else:
            page_title, page_content = wikisource_get_page_text(page_uri)
            page_content = remove_punctuation(page_content)
            with open(full_in_file_name, "w") as f:
                f.write(page_content)

        print("Generating word list...")
        words_list = Counter(page_content.split())
        print("Generating word list...Done.")
        with open(full_ou_file_name, "w") as flout:
            txt = "{| class=\"wikitable sortable\"\n|-\n"
            flout.write(txt)
            txt = "|+ {} માટેનું ભાષા વિશ્લેષણ \n|-\n".format(page_name)
            flout.write(txt)
            txt = "! ક્રમ !! સંખ્યા !! શબ્દ\n|-\n"
            flout.write(txt)
            grand_total = 0
            for i, word in enumerate(sorted(words_list, key=words_list.get, reverse=True), start=1):
                txt = "| {} || {}  || {} \n|-\n".format(i, words_list[word], word)
                grand_total += words_list[word]
                flout.write(txt)

            txt = "|}\n\n"
            flout.write(txt)
            unique_words = len(words_list.keys())
            txt = "કુલ {} શબ્દોના લખાણમાં અનન્ય શબ્દ {} છે.\n\n".format(grand_total, unique_words)
            flout.write(txt)
            print("Task over for {}.\n\n\n".format(page_name))


if __name__ == '__main__':
    main()
