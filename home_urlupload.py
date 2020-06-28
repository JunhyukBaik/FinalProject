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
#여기까지 파일체크
word_d = {}
sent_list = []

#URL예시
url_dic = {
        'https://ignite.apache.org/' : 400,
        'http://kafka.apache.org/' : 350,
        'http://helix.apache.org/' : 240,
        'http://madlib.apache.org/' : 260
        }
words_list = []

url_list = []

url_sent_list = []

word_count = []

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
            page = crawling_page(singleurl)
            process_newsentence(page)
            #분석~


            #url목록 -> 크롤링 -> 딕셔너리 생성 -> 분석 -> URLresult.html 렌더
