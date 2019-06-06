from django.shortcuts import render
from django.http import JsonResponse
from collections import Counter
import datetime
import jieba
jieba.set_dictionary('final_mix/jieba_big_chinese_dict/dict.txt.big')

import twitch
helix = twitch.Helix('xlxzn6l41n4x7t549rex0tjdfyho4r')

import pandas as pd
df = pd.read_excel('final_mix/dataset/streamer.xlsx')

def show_index(request):
    return render(request,'test.html')

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
    return docs[0:10]

def get_videos(ename,videosCount):
    docs=[]
    count = videosCount
    videos = helix.user(ename).videos(first=int(count))
    for video in videos:
        content = {"title":video.title,"created_at":timeFormat(video.created_at),"id":video.id,"view_count":video.view_count,"thumbnail_url":video.thumbnail_url,"duration":video.duration}
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

    return JsonResponse({"content": content})



def show_result(request):
    video_id = request.GET['id']
    chat_comments = word_frequency(getChatComments(video_id))

    return render(request,'result.html',{"chat_comments":chat_comments})


def word_frequency(text):
    words = [word for word in jieba.lcut(text) if len(word) >= 2]
    c = Counter(words)
    wa = []
    ca = []
    for word_freq in c.most_common(5):
        word, count = word_freq
        wa.append(word)
        ca.append(count)

    data = {
        "labels": wa,
        "values": ca,
    }
    return data


def getChatComments(id):
    comments = helix.video(id).comments()
    text = ''
    for i in range(20):
        text += str(comments[i].message.body + ",")

    return text






