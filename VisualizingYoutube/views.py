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
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException
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
                # pprint.pprint(search_videos)
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
    'channelUrl',
    'title',
    'description',
    'videoId',
    'actualStartTime',
    'concurrentViewers',
]


class YoutubeLiveRanking(TemplateView):
    """YoutubeLiveランキング"""
    template_name = 'youtubelive_ranking.html'

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
            maxResults=20,
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

            for search_video_result in search_video.get("items", []):
                se = pd.Series([
                    search_video_result['snippet']['channelTitle'],
                    'https://www.youtube.com/channel/' + search_video_result['snippet']['channelId'],
                    search_video_result['snippet']['title'],
                    search_video_result['snippet']['description'],
                    search_video_result['id'],
                    iso_to_jstdt(search_video_result['liveStreamingDetails']['actualStartTime']),
                    int(search_video_result['liveStreamingDetails']['concurrentViewers']),
                    ], live_columns)
                live_df = live_df.append(se, ignore_index=True)
        # 視聴者数が多い順にソート
        sorted_df = live_df.sort_values(['concurrentViewers'], ascending=False)

        context = {
            'sorted_df': sorted_df
        }

        return context


# ISO時間（文字列）を日本時間（datetime型）に変換
def iso_to_jstdt(iso_str: str) -> str:
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
    """ちくわちゃんランキング"""
    template_name = 'all_live_ranking.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(options=options)
        driver.get('http://www.chikuwachan.com/twicas/')
        html = driver.page_source

        soup = BeautifulSoup(html, 'lxml')
        live_list = []
        for i in range(1, 31):
            common_selector = f'#ranking > div > ul > li:nth-child({i}) > '
            title_selector = common_selector + 'div.content > a.liveurl > div.title'
            topic_selector = common_selector + 'div.content > a.liveurl > div.topic'
            href_selector = common_selector + 'div.content > a.liveurl'
            icon_selector = common_selector + 'div.content > a.liveurl > div.image_user > img'
            image_selector = common_selector + 'a > span > img'
            site_selector = common_selector + 'div.content > a.siteicon > img'
            viewers_selector = common_selector + 'div > div.count'
            progress_selector = common_selector + 'div.content > div.progress'

            if i < 11:
                live = {
                    # 'title': driver.find_element_by_css_selector(title_selector).text,
                    # 'topic': driver.find_element_by_css_selector(topic_selector).text,
                    # 'url': driver.find_element_by_css_selector(href_selector).get_attribute('href'),
                    # 'icon': driver.find_element_by_css_selector(icon_selector).get_attribute('src'),
                    # 'image': driver.find_element_by_css_selector(image_selector).get_attribute('src'),
                    # 'site': driver.find_element_by_css_selector(site_selector).get_attribute('src')
                    'title': soup.select_one(title_selector).get_text(),
                    'topic': soup.select_one(topic_selector).get_text(),
                    'url': soup.select_one(href_selector).get('href'),
                    'image': soup.select_one(image_selector).get('src'),
                    'icon': soup.select_one(icon_selector).get('src'),
                    'site': soup.select_one(site_selector).get('src'),
                    'viewers': soup.select_one(viewers_selector).get_text(),
                    'progress': soup.select_one(progress_selector).get_text()
                }
                live_list.append(live)
            else:
                live = {
                    # 'title': driver.find_element_by_css_selector(title_selector).text,
                    # 'topic': driver.find_element_by_css_selector(topic_selector).text,
                    # 'url': driver.find_element_by_css_selector(href_selector).get_attribute('href'),
                    # 'icon': driver.find_element_by_css_selector(icon_selector).get_attribute('data-src'),
                    # 'image': driver.find_element_by_css_selector(image_selector).get_attribute('data-src'),
                    # 'site': driver.find_element_by_css_selector(site_selector).get_attribute('src')
                    'title': soup.select_one(title_selector).get_text(),
                    'topic': soup.select_one(topic_selector).get_text(),
                    'url': soup.select_one(href_selector).get('href'),
                    'image': soup.select_one(image_selector).get('data-src'),
                    'icon': soup.select_one(icon_selector).get('data-src'),
                    'site': soup.select_one(site_selector).get('src'),
                    'viewers': soup.select_one(viewers_selector).get_text(),
                    'progress': soup.select_one(progress_selector).get_text()
                }
                live_list.append(live)
        live_df = pd.DataFrame(live_list)
        context = {
            'live_df': live_df
        }

        return context


class YoutubeRanking(TemplateView):
    """ちくわちゃんランキング"""
    template_name = 'youtube_ranking.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(options=options)
        driver.get('http://www.chikuwachan.com/live/TUB/')
        html = driver.page_source

        soup = BeautifulSoup(html, 'lxml')
        live_list = []
        for i in range(1, 31):
            common_selector = f'#ranking > div > ul > li:nth-child({i}) > '
            title_selector = common_selector + 'div.content > a.liveurl > div.title'
            topic_selector = common_selector + 'div.content > a.liveurl > div.topic'
            href_selector = common_selector + 'div.content > a.liveurl'
            icon_selector = common_selector + 'div.content > a.liveurl > div.image_user > img'
            image_selector = common_selector + 'a > span > img'
            site_selector = common_selector + 'div.content > a.siteicon > img'
            viewers_selector = common_selector + 'div > div.count'
            progress_selector = common_selector + 'div.content > div.progress'

            if i < 11:
                live = {
                    # 'title': driver.find_element_by_css_selector(title_selector).text,
                    # 'topic': driver.find_element_by_css_selector(topic_selector).text,
                    # 'url': driver.find_element_by_css_selector(href_selector).get_attribute('href'),
                    # 'icon': driver.find_element_by_css_selector(icon_selector).get_attribute('src'),
                    # 'image': driver.find_element_by_css_selector(image_selector).get_attribute('src'),
                    # 'site': driver.find_element_by_css_selector(site_selector).get_attribute('src')
                    'title': soup.select_one(title_selector).get_text(),
                    'topic': soup.select_one(topic_selector).get_text(),
                    'url': soup.select_one(href_selector).get('href'),
                    'image': soup.select_one(image_selector).get('src'),
                    'icon': soup.select_one(icon_selector).get('src'),
                    'site': soup.select_one(site_selector).get('src'),
                    'viewers': soup.select_one(viewers_selector).get_text(),
                    'progress': soup.select_one(progress_selector).get_text()
                }
                live_list.append(live)
            else:
                live = {
                    # 'title': driver.find_element_by_css_selector(title_selector).text,
                    # 'topic': driver.find_element_by_css_selector(topic_selector).text,
                    # 'url': driver.find_element_by_css_selector(href_selector).get_attribute('href'),
                    # 'icon': driver.find_element_by_css_selector(icon_selector).get_attribute('data-src'),
                    # 'image': driver.find_element_by_css_selector(image_selector).get_attribute('data-src'),
                    # 'site': driver.find_element_by_css_selector(site_selector).get_attribute('src')
                    'title': soup.select_one(title_selector).get_text(),
                    'topic': soup.select_one(topic_selector).get_text(),
                    'url': soup.select_one(href_selector).get('href'),
                    'image': soup.select_one(image_selector).get('data-src'),
                    'icon': soup.select_one(icon_selector).get('data-src'),
                    'site': soup.select_one(site_selector).get('src'),
                    'viewers': soup.select_one(viewers_selector).get_text(),
                    'progress': soup.select_one(progress_selector).get_text()
                }
                live_list.append(live)
        youtube_live_df = pd.DataFrame(live_list)
        context = {
            'youtube_live_df': youtube_live_df
        }

        return context


class TwicasRanking(TemplateView):
    """ちくわちゃんランキング"""
    template_name = 'twicas_ranking.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(options=options)
        driver.get('http://www.chikuwachan.com/live/CAS/')
        html = driver.page_source

        soup = BeautifulSoup(html, 'lxml')
        live_list = []
        for i in range(1, 31):
            common_selector = f'#ranking > div > ul > li:nth-child({i}) > '
            title_selector = common_selector + 'div.content > a.liveurl > div.title'
            topic_selector = common_selector + 'div.content > a.liveurl > div.topic'
            href_selector = common_selector + 'div.content > a.liveurl'
            icon_selector = common_selector + 'div.content > a.liveurl > div.image_user > img'
            image_selector = common_selector + 'a > span > img'
            site_selector = common_selector + 'div.content > a.siteicon > img'
            viewers_selector = common_selector + 'div > div.count'
            progress_selector = common_selector + 'div.content > div.progress'

            if i < 11:
                live = {
                    # 'title': driver.find_element_by_css_selector(title_selector).text,
                    # 'topic': driver.find_element_by_css_selector(topic_selector).text,
                    # 'url': driver.find_element_by_css_selector(href_selector).get_attribute('href'),
                    # 'icon': driver.find_element_by_css_selector(icon_selector).get_attribute('src'),
                    # 'image': driver.find_element_by_css_selector(image_selector).get_attribute('src'),
                    # 'site': driver.find_element_by_css_selector(site_selector).get_attribute('src')
                    'title': soup.select_one(title_selector).get_text(),
                    'topic': soup.select_one(topic_selector).get_text(),
                    'url': soup.select_one(href_selector).get('href'),
                    'image': soup.select_one(image_selector).get('src'),
                    'icon': soup.select_one(icon_selector).get('src'),
                    'site': soup.select_one(site_selector).get('src'),
                    'viewers': soup.select_one(viewers_selector).get_text(),
                    'progress': soup.select_one(progress_selector).get_text()
                }
                live_list.append(live)
            else:
                live = {
                    # 'title': driver.find_element_by_css_selector(title_selector).text,
                    # 'topic': driver.find_element_by_css_selector(topic_selector).text,
                    # 'url': driver.find_element_by_css_selector(href_selector).get_attribute('href'),
                    # 'icon': driver.find_element_by_css_selector(icon_selector).get_attribute('data-src'),
                    # 'image': driver.find_element_by_css_selector(image_selector).get_attribute('data-src'),
                    # 'site': driver.find_element_by_css_selector(site_selector).get_attribute('src')
                    'title': soup.select_one(title_selector).get_text(),
                    'topic': soup.select_one(topic_selector).get_text(),
                    'url': soup.select_one(href_selector).get('href'),
                    'image': soup.select_one(image_selector).get('data-src'),
                    'icon': soup.select_one(icon_selector).get('data-src'),
                    'site': soup.select_one(site_selector).get('src'),
                    'viewers': soup.select_one(viewers_selector).get_text(),
                    'progress': soup.select_one(progress_selector).get_text()
                }
                live_list.append(live)
        twicas_live_df = pd.DataFrame(live_list)
        context = {
            'twicas_live_df': twicas_live_df
        }

        return context



import asyncio
from pornhub_api.backends.aiohttp import AioHttpBackend
from pornhub_api import PornhubApi
import pprint


class pornConfirm(TemplateView):
    template_name = 'porn_confirm.html'


class PornhubRanking(TemplateView):
    """Pornhubランキング"""
    template_name = 'pornhub_ranking.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        api = PornhubApi()
        video_ids =[]
        data = api.search.search(
            # "japanese",
            period="day",
            category=["japanese"]
            # tags=["japanese"],
            # ordering="rating"
            )
        THUMBNAIL_URL = 'https://ci.phncdn.com/'
        video_list = []
        for video in data.videos[:30]:
            data = {
                'title': video.title,
                'publish_date': video.publish_date,
                'views': video.views,
                'rating': float(video.rating),
                'duration': video.duration,
                'url': 'https://www.pornhub.com/view_video.php?' + video.url.query,
                'image1': THUMBNAIL_URL + video.thumbs[0].src.path,
                'image2': THUMBNAIL_URL + video.thumbs[2].src.path,
                'image3': THUMBNAIL_URL + video.thumbs[4].src.path,
                'image4': THUMBNAIL_URL + video.thumbs[6].src.path,
                'image5': THUMBNAIL_URL + video.thumbs[8].src.path,
                'image6': THUMBNAIL_URL + video.thumbs[10].src.path,
                'image7': THUMBNAIL_URL + video.thumbs[12].src.path,
                'image8': THUMBNAIL_URL + video.thumbs[14].src.path,
            }
            video_list.append(data)
        video_list_df = pd.DataFrame(video_list) #辞書のリストからDF生成
        video_list_df = video_list_df.sort_values(['rating','views'], ascending=False)

        context = {
            'video_list_df': video_list_df
        }
        return context

