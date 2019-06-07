from django.shortcuts import render
from django.http import JsonResponse
from collections import Counter
import os
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
    c = jiebaLcut(getChatComments(video_id,user_id))
    chart_chat_comments = word_frequency(c)
    cloud_chat_comments = cloud_frequency(c)


    return render(request,'result.html',{"chart_chat_comments":chart_chat_comments,"cloud_chat_comments":cloud_chat_comments})





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
            text += str(df2_comment[i])+","
    else:
        print("no file: get net")  #順便存檔
        comments = helix.video(video_id).comments()
        id = []
        comment = []
        for i in range(count):
            try:
                id.append(comments[i].commenter.display_name)
                comment.append(comments[i].message.body)
                text += str(comments[i].message.body)+","
                print(str(i)+" ---> "+id[i] + " : " + comment[i])
            except:
                break

        df2 = pd.DataFrame(columns=['id', 'comment'])
        df2['id'] = id
        df2['comment'] = comment

        df2.to_excel('final_mix/dataset/videos/'+user_id+'/'+video_id+'.xlsx')
        print('save file '+video_id)

    return text











