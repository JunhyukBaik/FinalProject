#!/usr/bin/python3
import re
import requests
import numpy
import math
from nltk import word_tokenize
from flask import Flask, render_template, request
from bs4 import BeautifulSoup

app = Flask(__name__)

word_d = {}
sent_list = []

#URL예시
url_dic = {
        'https://ignite.apache.org/' : 400,
        'http://kafka.apache.org/' : 350,
        'http://helix.apache.org/' : 240,
        'http://madlib.apache.org/' : 260
        }
url_list = []

def url_input_list(dic):
    for key in dic.keys():
        url_list.append(key)

def crawling_page(urllist):
    for url in urllist:
        page = requests.get(url)
        

def process_newsentence(s):
    sent_list.append(s)
    tokenized = word_tokenize(s)
    for word in tokenized:
        if word not in word_d.keys():
            word_d[word] = 0
        word_d[word] += 1

def make_vector(i):
    v = []
    s = sent_list[i]
    tokenized = word_tokenize(s)
    for w in word_d.keys():
        val = 0
        for t in tokenized:
            if t == w:
                val += 1
        v.append(val)
    return v

def calcul_cossim(s1,s2):
    process_new_sentence(s1)
    process_new_sentence(s2)
    v1 = make_vector(0)
    v2 = make_vector(1)
    dotpro = numpy.dot(v1,v2)
    cossim = dotpro / (numpy.linalg.norm(v1) * numpy.linalg.norm(v2))
    word_d = {}
    sent_list = []
    return cossim

def compute_tf(s):
    bow = set()
    wordcount_d = {}

    tokenized = word_tokenize(s)
    for tok in tokenized:
        if tok not in wordcount_d.keys():
            wordcount_d[tok] = 0
        wordcount_d[tok] += 1
        bow.add(tok)

    tf_d = {}
    for word,count in wordcount_d.items():
        tf_d[word] = count / float(len(bow))

    return tf_d

def compute_idf():
    Dval = len(sent_list)
    bow = set()

    for i in range(0,len(sent_list)):
        tokenized = word_tokenize(sent_list[i])
        for tok in tokenized:
            bow.add(tok)

    idf_d = {}
    for t in bow:
        cnt = 0.1
        for s in sent_list:
            if t in word_tokenize(s):
                cnt += 1
            idf_d[t] = math.log(Dval / float(cnt))

    return idf_d

def calcul_tfidf(s,num):
    for i in s:
        process_new_sentence(s[i])
    idf_d = compute_idf()
    tf_d = compute_tf(sent_list[num])
    freq = {}
    for word, tfval in tf_d.items():
        freq[word] = tfval*idf_d[word]
    return freq

