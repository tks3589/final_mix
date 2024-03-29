from django.shortcuts import render
from django.http import JsonResponse
from collections import Counter
from snownlp import SnowNLP
import os
import datetime

from gensim.models.doc2vec import Doc2Vec
keyword_model = Doc2Vec.load("final_mix/dataset/model/comments_strTag.model")

import jieba
jieba.set_dictionary('final_mix/jieba_big_chinese_dict/dict.txt.big')

import twitch
helix = twitch.Helix('xlxzn6l41n4x7t549rex0tjdfyho4r')

import pandas as pd
df = pd.read_excel('final_mix/dataset/streamer.xlsx')


def show_index(request):
    return render(request,'test.html')

def show_keywordVideo(request):
    return render(request,'keywordVideo.html')



def api_cat_streamer(request):
    cat = request.GET['category']
    content = get_cat_streamer(cat=cat)
    #print(content)
    return JsonResponse({"content": content})


def get_cat_streamer(cat="遊戲"):
    docs=[]
    df_cat = df[df.category == cat]
    for i in range(len(df_cat)):
        content = {"sid": df_cat.iloc[i].sid, "category": df_cat.iloc[i].category,
                   "sname": df_cat.iloc[i].sname }
        docs.append(content)
    return docs[0:20]

def get_videos(ename,videosCount):
    docs=[]
    count = videosCount
    videos = helix.user(ename).videos(first=int(count))
    for video in videos:
        content = {"title":video.title,"created_at":timeFormat(video.created_at),"id":video.id,"view_count":video.view_count,"thumbnail_url":video.thumbnail_url,"duration":video.duration,"ename":ename}
        docs.append(content)

    return docs[0:int(count)]

def timeFormat(utc):
    UTC_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
    utcTime = datetime.datetime.strptime(utc, UTC_FORMAT)
    localtime = utcTime + datetime.timedelta(hours=8)

    return str(localtime)


def api_streamer_videos(request):
    sid = request.GET['streamer_id']
    videosCount = request.GET['videosCount']
    itemdf = df[df.sid == sid]
    ename = itemdf.iloc[0].ename
    #content = {"ename":ename}
    content = get_videos(ename,videosCount)
    checkVideo = get_exist_videos(ename)

    return JsonResponse({"content": content,"checkVideo":checkVideo})

def get_exist_videos(ename):
    exist_videos = []
    dirpath = 'final_mix/dataset/videos/' + ename
    if os.path.isdir(dirpath):
        for video in os.listdir(dirpath):
            #print(video[0:9])
            exist_videos.append(video[0:9])


    return exist_videos





def show_result(request):
    video_id = request.GET['id']
    user_id = request.GET['username']
    video_title = helix.video(video_id).title
    chat_text = getChatComments(video_id,user_id)
    c = jiebaLcut(chat_text)
    chart_chat_comments = word_frequency(c)
    cloud_chat_comments = cloud_frequency(c)
    sentences_senti_count = get_sentiment(chat_text)

    goodmanData,badmanData = get_viewers_sentiment(user_id,video_id)

    return render(request,'result.html',{"video_title":video_title,"chart_chat_comments":chart_chat_comments,
                                          "cloud_chat_comments":cloud_chat_comments,"sentences_senti_count":sentences_senti_count,
                                          "goodmanData":goodmanData,"badmanData":badmanData})
    # return render(request,'result.html',{"chart_chat_comments":chart_chat_comments,
    #                                      "cloud_chat_comments":cloud_chat_comments,"sentences_senti_count":sentences_senti_count})



def word_frequency(c):
    wa = []
    ca = []
    for word_freq in c.most_common(10):
        word, count = word_freq
        wa.append(word)
        ca.append(count)

    data = {
        "labels": wa,
        "values": ca,
    }
    return data


def cloud_frequency(c):
    data = []
    for word_freq in c.most_common(10):
        word, count = word_freq
        collection = []
        collection.append(word)
        collection.append(count)
        data.append(collection)

    return data


def jiebaLcut(text):
    words = [word for word in jieba.lcut(text) if len(word) >= 2 and len(word) <= 10]
    c = Counter(words)

    return c


def getChatComments(video_id,user_id): #判斷net or local
    count = 200 #撈的訊息筆數
    text = ''
    dirpath = 'final_mix/dataset/videos/'+user_id
    if os.path.isdir(dirpath):
        print(dirpath + ' is exit')
    else:
        os.mkdir(dirpath)
        print(dirpath + ' is created')

    filepath = 'final_mix/dataset/videos/'+user_id+'/'+video_id+'.xlsx'
    if os.path.isfile(filepath):
        print("file is exist: get local")
        df2 = pd.read_excel(filepath)
        df2_comment = df2['comment']
        for i in range(len(df2_comment)):
            text += str(df2_comment[i])+"，"

    else:
        print("no file: get net")  #順便存檔
        comments = helix.video(video_id).comments()
        id = []
        comment = []
        for i in range(count):
            try:
                display_name = str(comments[i].commenter.display_name)
                viewer_comment = str(comments[i].message.body)
                id.append(display_name)
                comment.append(viewer_comment)
                text += viewer_comment+"，"
                print(str(i)+" ---> "+id[i] + " : " + comment[i])
            except:
                break

        df2 = pd.DataFrame(columns=['id', 'comment'])
        df2['id'] = id
        df2['comment'] = comment

        df2.to_excel('final_mix/dataset/videos/'+user_id+'/'+video_id+'.xlsx')
        print('save file '+video_id)

    return text


def get_sentiment(text):
    sentences_senti_count = {'pos': 0, 'neg': 0, 'obj': 0}
    if len(text) == 0:
        return
    snow = SnowNLP(text)
    for sen in snow.sentences:
        #print(sen)
        snow2 = SnowNLP(sen)
        senti = snow2.sentiments
        if senti > 0.6:
            sentences_senti_count['pos'] += 1
        elif senti < 0.4:
            sentences_senti_count['neg'] += 1
        else:
            sentences_senti_count['obj'] += 1
        print(str(sen)+"----->"+str(senti))

    return sentences_senti_count




def get_viewers_sentiment(user_id,video_id):
    filepath = 'final_mix/dataset/videos/' + user_id + '/' + video_id + '.xlsx'
    df = pd.read_excel(filepath)
    df_viewer = df['id']
    df_comment = df['comment']
    good = []
    bad = []
    for i in range(len(df_viewer)):
        snow = SnowNLP(str(df_comment[i]))
        senti = snow.sentiments
        if senti > 0.6:
            good.append(df_viewer[i])
        elif senti < 0.4:
            bad.append(df_viewer[i])

    gc = Counter(good)
    bc = Counter(bad)
    goodman = []
    badman = []
    goodComments = []
    badComments = []
    for word_freq in gc.most_common(3):
        word, count = word_freq
        #print(count)
        goodman_cat = df[df.id == word]
        for i in range(len(goodman_cat)):
            snow = SnowNLP(str(goodman_cat.iloc[i].comment))
            senti = snow.sentiments
            if senti > 0.6:
                goodComments.append(goodman_cat.iloc[i].comment)
        goodman.append((word,count,goodComments))
        goodComments = []

    for word_freq in bc.most_common(3):
        word, count = word_freq
        badman_cat = df[df.id == word]
        for i in range(len(badman_cat)):
            snow = SnowNLP(str(badman_cat.iloc[i].comment))
            senti = snow.sentiments
            if senti < 0.4:
                badComments.append(badman_cat.iloc[i].comment)
        badman.append((word,count,badComments))
        badComments = []

    return goodman,badman


def api_get_keywordVideo(request):
    word = request.GET['keyword']
    keyword = []
    keyword.append(str(word))
    vec = keyword_model.infer_vector(keyword)
    keywordVideoData = keyword_model.docvecs.most_similar([vec], topn=10)
    filepath = 'final_mix/dataset/comments_doc2vec.xlsx'
    read_df = pd.read_excel(filepath)
    docs = []

    for data in keywordVideoData:
        vid = int(data[0])
        rate = round(float(data[1]),3)
        itemdf = read_df[read_df.vid == vid]
        cname = itemdf.iloc[0].cname
        title = itemdf.iloc[0].title
        img = itemdf.iloc[0].img
        content = {"vid": vid, "cname": cname, "title": title, "img": img,"rate":rate}
        docs.append(content)


    return JsonResponse({"keywordVideoData": docs})

















