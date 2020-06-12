from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView
from django.http import Http404, HttpResponse
from django.conf import settings
# from .forms import LiveSearchForm
import requests
import logging
import pandas as pd
from datetime import datetime
import pytz
import pprint

from apiclient.discovery import build
from apiclient.errors import HttpError
# from oauth2client.tools import argparser

# YouTube APIの各種設定
YOUTUBE_API_KEY = settings.YOUTUBE_API_KEY
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# dataframeのカラム定義
columns = [
    'channelTitle',
    'title',
    'description',
    'videoId',
    'actualStartTime',
    'concurrentViewers',
]

class videoSearch(TemplateView):
    template_name = 'video_search.html'


class liveRanking(TemplateView):
    template_name = 'live_ranking.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        # Youtubeインスタンス作成
        youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                        developerKey=YOUTUBE_API_KEY)
        search_response = youtube.search().list(
            # q='ThtcrBgB4KY',
            regionCode='JP',
            eventType='live',
            type='video',
            part='id,snippet',
            order='viewCount',
            maxResults=15,
        ).execute()

        videos = []
        for search_result in search_response.get("items", []):
            if search_result['snippet']['liveBroadcastContent'] == 'live':
                videos.append(search_result['id']['videoId'])

        live_df = pd.DataFrame(columns=columns)
        for video in videos:
            search_video = youtube.videos().list(
                id=video,
                part='id, snippet, liveStreamingDetails, player, statistics',
                maxResults=1,
                regionCode='JP',
            ).execute()
            print(search_video)
            for search_video_result in search_video.get("items", []):
                se = pd.Series([
                    search_video_result['snippet']['channelTitle'],
                    search_video_result['snippet']['title'],
                    search_video_result['snippet']['description'],
                    search_video_result['id'],
                    iso_to_jstdt(search_video_result['liveStreamingDetails']['actualStartTime']),
                    int(search_video_result['liveStreamingDetails']['concurrentViewers']),
                    ], columns)
                live_df = live_df.append(se, ignore_index=True)
        # 視聴者数が多い順にソート
        sorted_df = live_df.sort_values(['concurrentViewers'], ascending=False)

        print(sorted_df)

        context = {
            'sorted_df': sorted_df
        }

        return context


# ISO時間（文字列）を日本時間（datetime型）に変換
def iso_to_jstdt(iso_str):
    dt = None
    try:
        dt = datetime.strptime(iso_str, '%Y-%m-%dT%H:%M:%S.%fZ')
        dt = pytz.utc.localize(dt).astimezone(pytz.timezone("Asia/Tokyo"))
    except ValueError:
        try:
            dt = datetime.strptime(iso_str, '%Y-%m-%dT%H:%M:%S.%f%z')
            dt = dt.astimezone(pytz.timezone("Asia/Tokyo"))
        except ValueError:
            pass
    return dt
