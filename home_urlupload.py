#!/usr/bin/python3
from flask import Flask, request, render_template, url_for
import urllib.request
from bs4 import BeautifulSoup
import re
import os
from werkzeug import secure_filename
app = Flask(__name__)
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
def crawling_page(urllist):
    for url in urllist:
        page = requests.get(url)
    return page
        

def process_newsentence(s):
    sent_list.append(s)
    tokenized = word_tokenize(s)
    for word in tokenized:
        if word not in word_d.keys():
            word_d[word] = 0
        word_d[word] += 1

sent_list = []
word_d = {}

@app.route('/')
def home():
    return render_template('OSP_finhome.html')

@app.route('/result', methods = ['GET', 'POST'])
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
                    page = crawling_page(urls)
                    process_newsentences(page)
                #분석~
        else: #단일
            page = crawling_page(singleurl)
            process_newsentence(page)
            #분석~


            #url목록 -> 크롤링 -> 딕셔너리 생성 -> 분석 -> URLresult.html 렌더
