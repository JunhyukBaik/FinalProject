#!/usr/bin/python3
from flask import Flask, request, render_template, url_for
import urllib.request
from bs4 import BeautifulSoup
import re
import os
from werkzeug import secure_filename
import requests
import numpy
import time
import math
from nltk import word_tokenize
from elasticsearch import Elasticsearch
from elasticsearch import helpers

app = Flask(__name__)

es_host = "127.0.0.1"
es_port = "9200"
index_name = "crawling"
es = Elasticsearch([{"host": es_host, "port": es_port}], timeout=30)

app.config['MAX_CONTENT_LENGTH'] = 16*1024*1024
UPLOAD_FOLDER = './uploads/'
ALLOWED_EXTENSIONS = set(['txt'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
def read_uploaded_file():
    filename = secure_filename(request.args.get('filename'))
    try:
        if filename and allowed_filename(filename):
            with open(os.path.join(app.config['UPLOAD_FOLDER'], filename)) as f:
                return f.readlines()
    except IOError:
        pass
    return "Unable to read file"



word_d = {}
sent_list = []

#단어 수 리스트
words_list = []

#URL만 따로 리스트에 정리
url_list = []

#크롤링 한문장으로 만들어 놓은것
url_sent_list = []

#TF-IDF Top10단어 2차원 리스트
word_count = []

#시간 리스트
chk_time1 = []
chk_time2 = []
add_time = []


def word_cnt(sentence_list):
    for sent in sentence_list:
        emptylist = sent.split()
        cnt = len(emptylist)
        words_list.append(cnt)


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
        ntime = time.time() - start
        chk_time1.append(ntime)
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

def make_index(es, index_name):
     if es.indices.exists(index=index_name):
      es.indices.delete(index=index_name)
      es.indices.create(index=index_name)

    #print(es.indices.create(index = index_name))


def insertData(es, index_name): 
    if len(url_list) == 1:
      for i in range(0, len(url_list)):
         body = {
            'url' : url_list[i],
            'word_count' : words_list[i],
            'runtime' : add_time[i]
         }
         es.index(index = index_name, id = i+1, body = body)
   else:
      for i in range(0, len(url_list)):
         body = {
            'url' : url_list[i],
            'word_count' : words_list[i],
            'runtime' : add_time[i],
            'top3' : cos_url[i],
            'top10' : word_count[i]
         }
         es.index(index = index_name, id = i+1, body = body)


def searchDB():
    index = index_for_search
    body = {
            "query": {
                "match_all": {}
                }
            }

    result =  es.search(index = index, body = body)


@app.route('/') #디폴트페이지
def home():
    return render_template('OSP_finhome.html')

@app.route('/result', methods = ['GET', 'POST'])#버튼/업로드
def upload():
    if request.method == 'POST':
        file = request.files['file'] #단일url
        singleurl = request.form['singleurl'] #파일
        if singleurl == '':#파일일때
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                lsts = read_uploaded_file()
                if lsts == "Unable to read file":
                    return redirect(request.url)
                
                for urls in lsts:
                    url_list.append(urls)
                #분석~
        else: #단일
            url_list.append(singleurl)

    crawling_page(url_list)
 
    es = Elasticsearch([{'host':es_host, 'port':es_port}], timeout = 30)
    make_index(es, index_name)
    insertData(es, index_name)

    cossim_list = []
    cossim_inlist = []


    
    for i in range(len(url_sent_list)):
        start = time.time()
        for j in range(len(url_sent_list)): 
            cos = calcul_cossim(url_sent_list[i], url_sent_list[j])
            cossim_inlist.append(cos)
        cossim_list.append(cossim_inlist)
        cossim_inlist = []
        ntime = time.time() - start
        chk_time2.append(ntime)
    
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
    add_time = [x+y for x,y in zip(chk_time1, chk_time2)]
    
    
    return render_template('URLresult.html', urllist=url_list, wordnum=words_list, coslist=cos_url, tflist=word_count, timelist=add_time)
