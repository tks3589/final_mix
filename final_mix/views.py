from django.shortcuts import render
from django.http import JsonResponse

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

def get_videos(ename):
    docs=[]
    count = 10
    videos = helix.user(ename).videos(first=count)
    for video in videos:
        content = {"title":video.title,"created_at":video.created_at,"id":video.id,"view_count":video.view_count,"thumbnail_url":video.thumbnail_url}
        docs.append(content)

    return docs[0:count]

def api_streamer_videos(request):
    sid = request.GET['streamer_id']
    itemdf = df[df.sid == sid]
    ename = itemdf.iloc[0].ename
    #content = {"ename":ename}
    content = get_videos(ename)

    return JsonResponse({"content": content})



