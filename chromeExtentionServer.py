# -*- coding: utf-8 -*-
import os
import json
import sys
import tweepy
import hashlib
from flask import Flask, session, redirect, render_template, request, jsonify, abort, make_response
from flask_cors import CORS, cross_origin
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
# import sqlalchemy
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy import Column, Integer, String, DATETIME
# from sqlalchemy.orm import *
# from sqlalchemy import exc
from datetime import datetime
import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
import MeCab
import gensim
import numpy as np
import cchardet

mecab = MeCab.Tagger('-d /usr/local/lib/mecab/dic/mecab-ipadic-neologd')
mecab.parse('')
model = gensim.models.KeyedVectors.load_word2vec_format('cc.ja.300.bin', binary=True)
# model = gensim.models.KeyedVectors.load_word2vec_format('cc.ja.300.bin', binary=True)
# model.save_word2vec_format('cc.ja.300.bin', binary=True)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///highlight.sqlite3?check_same_thread=False'
db = SQLAlchemy(app)
# from marshmallow_sqlalchemy import ModelSchema
# engine = sqlalchemy.create_engine('sqlite:///highlight.sqlite3', connect_args={'check_same_thread': False})
ma = Marshmallow(app)
CORS(app)
# Base = declarative_base()
class Entry(db.Model):
    __tablename__ = "highlight"
    id = db.Column('id', db.Integer, primary_key=True)
    userID = db.Column("userid", db.String(120), nullable=False)
    url = db.Column('url', db.String(120))
    nowTime = db.Column("nowTime", db.String(120), nullable=False)
    parentDom = db.Column("parentDom", db.String(120), nullable=False)
    selectText = db.Column("selectText", db.String(120), nullable=False)
    # parentElementText = db.Column("parentElementText", db.String(120), nullable=False)
    # tagName = db.Column('tagName', db.String(120), nullable=False)
    flag = db.Column('flag', db.Boolean, unique=False, default=True)
    pageTitle = db.Column('pageTitle', db.String(120), nullable=False)
class EntrySchema(ma.ModelSchema):
    class Meta:
        model = Entry
# Base.metadata.create_all(bind=engine)
# DBSession = sessionmaker(
#     autocommit = False,
#     autoflush = True,
#     bind = engine)
# dbSession = DBSession()

app.secret_key = ""
# --------------------------------------------------------------------------

CONSUMER_KEY = ""
CONSUMER_SECRET = ""

# --------------------------------------------------------------------------

# @app.route("/oath", methods=["GET"])
# @cross_origin()
# def oath():
#     auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
#     try:
#         # 連携アプリ認証用の URL を取得
#         redirect_url = auth.get_authorization_url()
#         session['request_token'] = auth.request_token
#     except Exception as ee:
#         # except tweepy.TweepError:
#         sys.stderr.write("*** error *** twitter_auth ***\n")
#         sys.stderr.write(str(ee) + "\n")
#     return redirect_url

# def getUserId(auth):
#     api = tweepy.API(auth)
#     me = api.me()
#     return me.id

# @app.route("/twitter", methods=['GET'])
# @cross_origin()
# def twitter():
#     auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
#     verifier = request.args.get('oauth_verifier')
#     request_token = request.args.get("oauth_token")
#     auth.request_token['oauth_token'] = str(request_token)
#     auth.request_token['oauth_token_secret'] = str(verifier)
#     try:
#         auth.get_access_token(str(verifier))
#     except Exception as ee:
#         print("error", ee)
#     now = datetime.now()
#     unix = int(time.mktime(now.timetuple()))
#     userId= getUserId(auth)
#     api = tweepy.API(auth)
#     userName = api.get_user(userId)
#     entry = Entry(ID = str(unix) + str(userId), userID = str(userId), name=str(userName.name), access_token=str(auth.access_token), access_token_secret=str(auth.access_token_secret))
#     dbSession.add(entry)
#     try:
#         dbSession.commit()
#         return redirect("https://adoring-dubinsky-d79ae4.netlify.com/TwitterForm" + "?Id={}".format(str(unix)))
#     except exc.IntegrityError as e:
#         print(e)

# @app.route("/get_name", methods=["GET"])
# @cross_origin()
# def get_name():
#     res = request.args
#     Id = res.get("id")
#     print(Id)
#     answer = dbSession.query(Entry).filter(Entry.ID == str(Id)+ Entry.userID).one()
#     name = answer.name
#     return jsonify({'name': name})

@app.route("/push_data", methods=["POST"])
@cross_origin()
def push_data():
    res = request.json
    print(res['userId'])
    user_id = res['userId']
    url = res["url"]
    select_text = res["selectText"]
    parent_element_text = res['parentDom']
    now_time = res['nowTime']
    page_title = res['pageTitle']
    # tag_name = res['tagName']
    # nowTime = int(time.mktime(datetime.now().timetuple()))
    print(time)
    entry = Entry(userID = str(user_id), url = str(url), nowTime=str(now_time), selectText=str(select_text), parentDom=str(parent_element_text),pageTitle=str(page_title))
    db.session.add(entry)
    try:
        db.session.commit()
        return 'ok'
    except Exception as error:
        print(error.orig)
    # except exc.IntegrityError as e:
    #     print(e)
    #     return 'error'

# @app.route('/sub', methods=['GET'])
# @cross_origin()
# def sub():
#     try:
#         res = request.args
#         print(res)
#         Id = res.get("Id")
#         data = dbSession.query(Entry).filter(Entry.ID == str(Id)+ Entry.userID).one()
#         data.verificationNum = data.verificationNum + 1
#         dbSession.add(data)
#         dbSession.commit()
#         print(data.verificationNum)
#         if data.confirmNum <= data.verificationNum:
#             auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
#             auth.set_access_token(data.access_token, data.access_token_secret)
#             api = tweepy.API(auth)
#             api.update_status(data.message)
#             dbSession.commit()
#         print("ok")
#         return "OK"
#     except Exception as ee:
#         print("error", ee)
    
@app.route('/changeFlag', methods=['POST'])
@cross_origin()
def chageFlag():
    res = request.json
    change = res['change']
    if change == 'change_false_all':
        answer = db.session.query(Entry).filter(Entry.flag == True).all()
        for data in answer:
            data.flag = False
    elif change == 'change_true':
        user_id = res['userId']
        url = res['url']
        time = res['time']
        answer = db.session.query(Entry).filter(Entry.userID == str(user_id), Entry.url == str(url), Entry.nowTime == str(time)).one()
        answer.flag = True
    elif change == 'change_false':
        user_id = res['userId']
        url = res['url']
        time = res['time']
        answer = db.session.query(Entry).filter(Entry.userID == str(user_id), Entry.url == str(url), Entry.nowTime == str(time)).one()
        answer.flag = False
    try:
        db.session.commit()
        print('ok')
        return 'ok'
    except Exception as error:
        print(error)

@app.route("/getData", methods=['POST'])
@cross_origin()
def selectDataToDatabase():
    res = request.json
    user_id = res["userId"]
    print(user_id)
    url = res["url"]
    print(url)
    entries_schema = EntrySchema(many=True)
    # test = dbSession.query(Entry.domData).filter(Entry.userID == str(userId), Entry.url == str(url)).all()
    # print(test)
    answer = db.session.query(Entry.parentDom, Entry.selectText, Entry.nowTime, Entry.url, Entry.flag).filter(Entry.userID == str(user_id), Entry.url == str(url)).all()
    print("answer", answer)
    return jsonify({'entries': entries_schema.dump(answer)})

@app.route("/getAllData", methods=['POST'])
@cross_origin()
def selectAllDataToDatabase():
    res = request.json
    user_id = res["userId"]
    print(user_id)
    entries_schema = EntrySchema(many=True)
    # test = dbSession.query(Entry.domData).filter(Entry.userID == str(userId), Entry.url == str(url)).all()
    # print(test)
    answer = db.session.query(Entry.parentDom, Entry.selectText, Entry.nowTime, Entry.url, Entry.pageTitle, Entry.flag).filter(Entry.userID == str(user_id)).all()
    print("answer", answer)
    return jsonify({'entries': entries_schema.dump(answer)})

@app.route("/getPositiveData", methods=['POST'])
@cross_origin()
def selectPositiveDataToDatabase():
    res = request.json
    user_id = res["userId"]
    print(user_id)
    url = res["url"]
    print(url)
    entries_schema = EntrySchema(many=True)
    # test = dbSession.query(Entry.domData).filter(Entry.userID == str(userId), Entry.url == str(url)).all()
    # print(test)
    answer = db.session.query(Entry.parentDom, Entry.selectText, Entry.nowTime, Entry.url, Entry.pageTitle).filter(Entry.userID == str(user_id), Entry.url == str(url), Entry.flag == True).all()
    print("answer", answer)
    return jsonify({'entries': entries_schema.dump(answer)})

@app.route("/getNegativeData", methods=['POST'])
@cross_origin()
def selectNegaDataToDatabase():
    res = request.json
    user_id = res["userId"]
    print(user_id)
    url = res["url"]
    print(url)
    entries_schema = EntrySchema(many=True)
    # test = dbSession.query(Entry.domData).filter(Entry.userID == str(userId), Entry.url == str(url)).all()
    # print(test)
    answer = db.session.query(Entry.parentDom, Entry.selectText, Entry.nowTime, Entry.url, Entry.pageTitle).filter(Entry.userID == str(user_id), Entry.url != str(url), Entry.flag == True).all()
    print("answer", answer)
    return jsonify({'entries': entries_schema.dump(answer)})

@app.route('/deleteData', methods=['POST'])
@cross_origin()
def deleteData():
    res = request.json
    user_id = res['userId']
    url = res['url']
    time = res['time']
    print(user_id, url, time)
    answer = db.session.query(Entry).filter(Entry.userID == str(user_id), Entry.url == str(url), Entry.nowTime == str(time)).one()
    print(answer)
    try:
        db.session.delete(answer)
        db.session.commit()
        return 'ok'
    except Exception as error:
        print(error)

# テキストのベクトルを計算
def get_vector(text):
    # sum_vec = np.zeros(200)
    sum_vec = np.zeros(300) #ここが200のままだとsum_vec += model.wv[item.split('\t')[0]]の部分でbroadcastエラーになる。
    word_count = 0
    # python3.7.1だとparseToNodeメソッドでうまく形態素解析できないためparse()とsplitlines(), split()で書き直した
    node = mecab.parse(text).splitlines()
    for item in node:
        if item.split('\t')[0]=='EOS':
            break
        field = item.split('\t')[1].split(',')[0]
        if field == '名詞' or field == '動詞' or field == '形容詞':
            try:
                sum_vec += model.wv[item.split('\t')[0]]
                word_count += 1
            except KeyError as error:
                continue
    return sum_vec / word_count
 
 
# cos類似度を計算
def cos_sim(v1, v2):
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

def sentence_sim(sentence1, sentence2):
    v1 = get_vector(sentence1)
    v2 = get_vector(sentence2)
    return cos_sim(v1, v2)

@app.route('/scrapingData', methods=['POST'])
@cross_origin()
def scrapingData():
    try:
        res = request.json
        url = res['urls']
        print(url)
        user_id = res['userId']
        bookmark_text = db.session.query(Entry.selectText).filter(Entry.userID == str(user_id),Entry.flag == True).all()
        html=requests.get(url)
        html.encoding = cchardet.detect(html.content)['encoding']
        soup=BeautifulSoup(html.text,"html.parser")
        for script in soup(["script", "style"]):
            script.decompose()
        text=soup.get_text()
        lines= [line.strip() for line in text.splitlines()]
        text=[line for line in lines if line]
        sentence_sims = []
        sim = 0
        for sentence in text:
            sim = 0
            if len(sentence) >= 15:
                for bookmark in bookmark_text:
                    text_sim = sentence_sim(sentence, bookmark[0])
                    if text_sim != None:
                        sim += text_sim
                    #print(bookmark[0])
            sentence_sims.append([sentence, sim])
        sorted_sentence_sims = sorted(sentence_sims, key=lambda x: np.inf if np.isnan(x[1]) else x[1], reverse=True)
        print(sorted_sentence_sims)
        n = 0
        final_text = ''
        if len(sorted_sentence_sims) < 3:
            while n <= len(sorted_sentence_sims):
                final_text += sorted_sentence_sims[n][0] + '\n'
                n += 1
            return jsonify({'sentence': final_text})
        while n <= 3:
            final_text += sorted_sentence_sims[n][0] + '\n'
            n += 1
        return jsonify({'sentence': final_text})
    except Exception as error:
        print('error')
        return jsonify({'sentence': 'error'})

# @app.route('/scrapingData', methods=['POST'])
# @cross_origin()
# def scrapingData():
#     res = request.json
#     url = res['urls']
#     user_id = res['userId']
#     #bookmark_text = db.session.query(Entry.selectText).filter(Entry.userID == str(user_id),Entry.flag == True).all()
#     html=requests.get(url).text
#     soup=BeautifulSoup(html,"html.parser")
#     for script in soup(["script", "style"]):
#         script.decompose()
#     text=soup.get_text()
#     lines= [line.strip() for line in text.splitlines()]
#     text=[line for line in lines if line]
    # sentence_sim = []
    # sim = 0
    # for sentence in text:
    #     sim = 0
    #     for bookmark in bookmark_text:
    #         sim += sentence_sim(sentence, bookmark)
    
    #     sentence_sim.append([sentence, sim])
    # sorted_sentence_sim = sorted(sentence_sim, key=lambda x: x[1], reverse=True)
    # n = 0
    # final_text = []
    # while True:
    #     final_text.append(sorted_sentence_sim[n][0])
    #     n += 1
    return jsonify({'sentence': text})

# @app.teardown_appcontext
# def session_clear(exception):
#     if exception and Session.is_active:
#         session.rollback()
#     else:
#         pass
#     dbSession.close()

def main():
    app.debug = True
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
# --------------------------------------------------------------------------
if __name__ == "__main__":
    main()
# --------------------------------------------------------------------------