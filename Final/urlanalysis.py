#!/usr/bin/python3
import re
import requests
import numpy
import time
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
#단어 수 리스트
words_list = []

#URL만 따로 리스트에 정리
url_list = []

#크롤링 한문장으로 만들어 놓은것
url_sent_list = []

#TF-IDF Top10단어 2차원 리스트
word_count = []

#시간 리스트
chk_time = []

def word_cnt(sentence_list):
    for sent in sentence_list:
        emptylist = sent.split()
        cnt = len(emptylist)
        words_list.append(cnt)

def url_input_list(dic):
    for key in dic.keys():
        url_list.append(key)

def crawling_page(urllist):
    for url in urllist:
        url_sentence = []
        page = requests.get(url)
        html = BeautifulSoup(page.content, 'html.parser')
        p_data = html.find_all('p')
        for data in p_data:
            data = data.get_text().replace('\t', '').replace('\n', '').replace('\r', '').strip().rstrip()
            url_sentence.append(data)
        url_sentence2 = " ".join(url_sentence)
        url_sent_list.append(url_sentence2)

def process_new_sentence(s):
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
    word_d.clear()
    sent_list.clear()
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

def calcul_tfidf(urlsentlist):
    start = time.time()
    for url in urlsentlist:
        process_new_sentence(url)
    idf_d = compute_idf()
    for i in range(0,len(sent_list)):
        freq = {}
        word_icount = []
        tf_d = compute_tf(sent_list[i])
        for word, tfval in tf_d.items():
            freq[word] = tfval*idf_d[word]
        lists = sorted(freq.items(), key=lambda x:x[1], reverse=True)
        for wrd, score in lists[:10]:
            word_icount.append(wrd)
        word_count.append(word_icount)
    word_d.clear()
    sent_list.clear()
    ptime = time.time() - start
    chk_time.append(ptime)

@app.route('/')
def result_url():
    url_input_list(url_dic)
    crawling_page(url_list)
    cossim_list = []
    cossim_inlist = []
    
    for i in range(len(url_sent_list)):
        for j in range(len(url_sent_list)): 
            cos = calcul_cossim(url_sent_list[i], url_sent_list[j])
            cossim_inlist.append(cos)
        cossim_list.append(cossim_inlist)
        cossim_inlist = []
    
    #Cosine Similarity Top3 url index list
    cossim_index_list = []
   
    cossim_index = []
    for lst in cossim_list:
        cossim_index = sorted(range(len(lst)), key=lambda k: lst[k], reverse = True)
        del cossim_index[cossim_index.index(0)]
        cossim_index_list.append(cossim_index)
    
    #Cosine Similarity Top3 url list
    cos_url = []

    for lst in cossim_index_list:
        icos = []
        for idx in lst:
            aUrl = url_list[idx]
            icos.append(aUrl)
        cos_url.append(icos)

    calcul_tfidf(url_sent_list)
    word_cnt(url_sent_list)
    
    
    return render_template('URLresult.html', urllist=url_list, wordnum=words_list, coslist=cos_url, tflist=word_count, timelist=chk_time)
