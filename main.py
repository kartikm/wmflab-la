#!/usr/bin/env python3
# -*- coding: utf_8 -*-
#
"""
    Copyright    : 2020 August 3.
    Organization : VAU Soft Tech
    Project      : vauWSLA
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
import re
from itertools import count

count_gen = count(1)

"""
    For carrying out Language Analysis, we need only text, without any punctuation
    marks. The text we are targeting to process, has punctuation marks not only 
    limited to Gujarati Language but also from other languages. Manual inspection 
    revealed that there may be punctuation marks from English, Hindi and Sanskrit 
    Language as well. 
    Therefore, below a variable holding the list of all the punctuation marks in
    entire unicode set is created using dictionary comprehension.
"""
tbl = {i: " " for i in range(sys.maxunicode)
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
    remove all possible punctuation marks from the text. So that   
"""
def remove_punctuation(text):
    return text.translate(tbl)


"""
    Tried using re module's power to identify punctuations but somehow it is not 
    removing punctuations.
"""
def remove_punctuation2(text):
    return re.sub(u"[[:punct:]]", "", text)


def wikisourec_page_uri_generator():
    base_uri = 'https://gu.wikisource.org/wiki/'
    yield next(count_gen), 'પલકારા/માસ્તર_સાહેબ', base_uri + 'પલકારા/માસ્તર_સાહેબ'
    return


def wikisource_get_page_text(pg):
    print(F"Connecting to WikiSource to get the text for {pg}.")
    status = rq.get(pg)
    if status.status_code ==200:
        print(F"Connection Successful. Received the text.")
        pg_content = bs(status.text, 'html.parser')
        pgttl = pg_content.h1.text
        pgtxt = ""
        # print(pg_content.prettify())
        for i, j in enumerate(pg_content.find_all(class_="prp-pages-output")):
            # for i, j in enumerate(pg_content.find_all(id='bodyContent', limit=1)):
            # print(i, j)
            pgtxt = j.text
            break
    else:
        pgttl, pgtxt  = -1, ""

    return pgttl, pgtxt


def check_whether_text_from_the_page_is_already_downloaded(in_fl_nm):
    return os.path.exists(in_fl_nm)


def get_text_from_the_local_file(full_file_name):
    print("Local copy found. So using that copy.")
    with open(full_file_name) as f:
        text = f.read()
    return text


def main():
    for no, pgnm, pguri in wikisourec_page_uri_generator():
        pgnm = pgnm.translate({ord("/"): "_"})
        print(F"Processing started for {no} - {pgnm}")

        full_in_flnm = os.path.join(in_txt_dir, f"{pgnm}-in.txt")
        full_ou_flnm = os.path.join(out_txt_dir, f"{pgnm}-out.txt")
        if check_whether_text_from_the_page_is_already_downloaded(full_in_flnm):
            y = get_text_from_the_local_file(full_in_flnm)
        else:
            x, y = wikisource_get_page_text(pguri)
            y = remove_punctuation(y)
            with open(full_in_flnm, "w") as f:
                f.write(y)

        print("Generating word list...")
        words_list = Counter(y.split())
        print("Generating word list...Done.")
        with open(full_ou_flnm, "w") as flout:
            txt = "{| class=\"wikitable sortable\"\n"
            flout.write(txt)
            txt = "|-\n"
            flout.write(txt)
            txt = f"|+ {pgnm} માટેનું ભાષા વિશ્લેષણ \n"
            flout.write(txt)
            txt = "|-\n"
            flout.write(txt)
            txt = "! ક્રમ !! સંખ્યા !! શબ્દ\n"
            flout.write(txt)
            txt = "|-\n"
            flout.write(txt)
            grand_total = 0
            for i, word in enumerate(sorted(words_list, key=words_list.get, reverse=True), start=1):
                txt = F"| {i} || {words_list[word]:>7d}  || {word:} \n"
                grand_total += words_list[word]
                flout.write(txt)
                txt = "|-\n"
                flout.write(txt)

            txt = "|}\n\n"
            flout.write(txt)
            unique_words = len(words_list. keys())
            txt = f"કુલ {grand_total} શબ્દોના લખાણમાં અનન્ય શબ્દ {unique_words} છે.\n\n"
            flout.write(txt)
            print(F"Task over for {pgnm}.\n\n\n")

if __name__ == '__main__':
    main()
