from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView
from django.http import Http404, HttpResponse
from django.conf import settings
from .forms import VideoSearchForm
# from .forms import LiveSearchForm
import requests
import logging
import pandas as pd
from datetime import datetime
import pytz
from bs4 import BeautifulSoup
import pprint

from apiclient.discovery import build
from apiclient.errors import HttpError
# from oauth2client.tools import argparser

# YouTube APIの各種設定
YOUTUBE_API_KEY = settings.YOUTUBE_API_KEY
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# dataframeのカラム定義
video_columns = [
    'channelId',
    'channelTitle',
    'channelURL',
    'title',
    'description',
    'publishedAt',
    'videoId',
    'viewCount',
    'likeCount',
    'dislikeCount',
    'commentCount'
]

class videoSearch(TemplateView):
    """Youtube動画検索"""
    template_name = 'video_search.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        # Youtubeインスタンス作成
        youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                        developerKey=YOUTUBE_API_KEY, cache_discovery=False)
        form = VideoSearchForm(self.request.GET or None)
        if form.is_valid():
            # 入力フォームからkeyword,display_number取得
            keyword = form.cleaned_data.get('keyword')
            display_number = int(form.cleaned_data.get('display_number'))
            order = form.cleaned_data.get('order')
        context['form'] = form
        # videoIdのリストを定義
        videos = []
        # columns定義したDataFrameを作成
        video_df = pd.DataFrame(columns=video_columns)

        try:
            search_response = youtube.search().list(
                q=keyword,
                regionCode='JP',
                type='video',
                part='id,snippet',
                order=order,
                maxResults=display_number,
            ).execute()

            for search_result in search_response.get("items", []):
                if search_result["id"]["kind"] == "youtube#video" and search_result['snippet']['liveBroadcastContent'] == 'none':
                    videos.append(search_result['id']['videoId'])

            for video in videos:
                search_videos = youtube.videos().list(
                    id=video,
                    part='id, snippet, player, statistics',
                    maxResults=1,
                    regionCode='JP',
                ).execute()
                pprint.pprint(search_videos)
                for search_video in search_videos.get("items", []):
                    se = pd.Series([
                        search_video['snippet']['channelId'],
                        search_video['snippet']['channelTitle'],
                        'https://www.youtube.com/channel/' + search_video['snippet']['channelId'],
                        search_video['snippet']['title'],
                        search_video['snippet']['description'],
                        search_video['snippet']['publishedAt'],
                        search_video['id'],
                        int(search_video['statistics']['viewCount']),
                        int(search_video['statistics']['likeCount']),
                        int(search_video['statistics']['dislikeCount']),
                        int(search_video['statistics']['commentCount']),
                    ], video_columns)
                    video_df = video_df.append(se, ignore_index=True)
            # 再生回数で降順
            sorted_video_df = video_df.sort_values(['viewCount'], ascending=False)
            print(sorted_video_df['viewCount'])
            context = {
                'form': VideoSearchForm(),  # フォーム初期化
                'sorted_video_df': sorted_video_df
            }
            if order == 'date':
                messages.success(self.request, f'"{keyword}"を含み、最近公開された動画で再生数順に表示します。')
            else:
                messages.success(self.request, f'"{keyword}"を含み、全ての動画で再生数順に表示します。')
            return context

        except:
            # messages.error(self.request, 'エラーが発生しました。')
            return context


# dataframeのカラム定義
live_columns = [
    'channelTitle',
    'title',
    'description',
    'videoId',
    'actualStartTime',
    'concurrentViewers',
]

class liveRanking(TemplateView):
    """YoutubeLiveランキング"""
    template_name = 'live_ranking.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        # Youtubeインスタンス作成
        youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                        developerKey=YOUTUBE_API_KEY, cache_discovery=False)
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

        live_df = pd.DataFrame(columns=live_columns)
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
                    ], live_columns)
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


class AllliveRanking(TemplateView):
    """YoutubeLiveランキング"""
    template_name = 'all_live_ranking.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        # ちくわちゃんランキングからスクレイピング
        CHIKURAN_URL = 'http://www.chikuwachan.com/live/'
        html = requests.get(CHIKURAN_URL)
        soup = BeautifulSoup(html.text, "html.parser")
        topicsindex = soup.find('div', class_="lives")
        # topicsindex = soup.find('div', id='ranking')
        # topics = topicsindex.find_all('li', attrs={'class': 'lives'})
        # print(html.text)

        # columns定義したDataFrameを作成
        # yahoo_news_df = pd.DataFrame(columns=yahoo_comment_columns)
        # for topic in topics:
        #     se = pd.Series([
        #         topic.find('span', attrs={'class': 'newsFeed_item_rankNum'}).contents[0],
        #         topic.find('div', attrs={'class': 'newsFeed_item_title'}).contents[0],
        #         topic.find('em').contents[0],
        #         topic.find('a').get('href')
        #     ], yahoo_comment_columns
        #     )
        #     yahoo_news_df = yahoo_news_df.append(se, ignore_index=True)

        # context = {
        #     'twitter_trend_df': twitter_trend_df,
        #     'yahoo_news_df': yahoo_news_df
        # }
        return context
