import logging
from datetime import datetime
from typing import Optional

import pandas as pd
import pytz

# from .forms import LiveSearchForm
import requests
from apiclient.discovery import build
from apiclient.errors import HttpError
from bs4 import BeautifulSoup
from django.conf import settings
from django.contrib import messages
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    TemplateView,
    UpdateView,
)
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from .forms import VideoIdForm, VideoSearchForm

logger = logging.getLogger(__name__)

# YouTube APIの各種設定
YOUTUBE_API_KEY = settings.YOUTUBE_API_KEY
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"


class videoSearch(TemplateView):
    """Youtube動画検索"""

    template_name = "video_search.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        # Youtubeインスタンス作成
        youtube = build(
            YOUTUBE_API_SERVICE_NAME,
            YOUTUBE_API_VERSION,
            developerKey=YOUTUBE_API_KEY,
            cache_discovery=False,
        )
        form = VideoSearchForm(self.request.GET or None)
        if form.is_valid():
            # 入力フォームからkeyword,display_number取得
            keyword = form.cleaned_data.get("keyword")
            display_number = int(form.cleaned_data.get("display_number"))
            order = form.cleaned_data.get("order")
        context["form"] = form
        # videoIdのリストを定義
        videos: list[str] = []
        # columns定義したDataFrameを作成
        video_columns = [
            "channelId",
            "channelTitle",
            "channelURL",
            "title",
            "description",
            "publishedAt",
            "videoId",
            "viewCount",
            "likeCount",
            "dislikeCount",
            "commentCount",
        ]

        video_df = pd.DataFrame(columns=video_columns)

        try:
            search_response = (
                youtube.search()
                .list(
                    q=keyword,
                    regionCode="JP",
                    type="video",
                    part="id,snippet",
                    order=order,
                    maxResults=display_number,
                )
                .execute()
            )

            for search_result in search_response.get("items", []):
                if (
                    search_result["id"]["kind"] == "youtube#video"
                    and search_result["snippet"]["liveBroadcastContent"] == "none"
                ):
                    videos.append(search_result["id"]["videoId"])

            for video in videos:
                search_videos = (
                    youtube.videos()
                    .list(
                        id=video,
                        part="id, snippet, player, statistics",
                        maxResults=1,
                        regionCode="JP",
                    )
                    .execute()
                )
                # pprint.pprint(search_videos)
                for search_video in search_videos.get("items", []):
                    se = pd.Series(
                        [
                            search_video["snippet"]["channelId"],
                            search_video["snippet"]["channelTitle"],
                            "https://www.youtube.com/channel/"
                            + search_video["snippet"]["channelId"],
                            search_video["snippet"]["title"],
                            search_video["snippet"]["description"],
                            search_video["snippet"]["publishedAt"],
                            search_video["id"],
                            int(search_video["statistics"]["viewCount"]),
                            int(search_video["statistics"]["likeCount"]),
                            int(search_video["statistics"]["dislikeCount"]),
                            int(search_video["statistics"]["commentCount"]),
                        ],
                        video_columns,
                    )
                    video_df = video_df.append(se, ignore_index=True)
            # 再生回数で降順
            sorted_video_df = video_df.sort_values(["viewCount"], ascending=False)
            context = {
                "form": VideoSearchForm(),  # フォーム初期化
                "sorted_video_df": sorted_video_df,
            }
            if order == "date":
                messages.success(self.request, f'"{keyword}"を含み、最近公開された動画で再生数順に表示します。')
            else:
                messages.success(self.request, f'"{keyword}"を含み、全ての動画で再生数順に表示します。')
            return context

        except:
            # messages.error(self.request, 'エラーが発生しました。')
            return context


class YoutubeLiveRanking(TemplateView):
    """YoutubeLiveランキング"""

    template_name = "youtubelive_ranking.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        # Youtubeインスタンス作成
        youtube = build(
            YOUTUBE_API_SERVICE_NAME,
            YOUTUBE_API_VERSION,
            developerKey=YOUTUBE_API_KEY,
            cache_discovery=False,
        )
        search_response = (
            youtube.search()
            .list(
                # q='ThtcrBgB4KY',
                regionCode="JP",
                eventType="live",
                type="video",
                part="id,snippet",
                order="viewCount",
                maxResults=20,
            )
            .execute()
        )

        videos: list[str] = []
        for search_result in search_response.get("items", []):
            if search_result["snippet"]["liveBroadcastContent"] == "live":
                videos.append(search_result["id"]["videoId"])

        # 生放送情報のカラム定義
        live_columns = [
            "channelTitle",
            "channelUrl",
            "title",
            "description",
            "videoId",
            "actualStartTime",
            "concurrentViewers",
        ]
        live_df = pd.DataFrame(columns=live_columns)
        for video in videos:
            search_video = (
                youtube.videos()
                .list(
                    id=video,
                    part="id, snippet, liveStreamingDetails, player, statistics",
                    maxResults=1,
                    regionCode="JP",
                )
                .execute()
            )

            for search_video_result in search_video.get("items", []):
                se = pd.Series(
                    [
                        search_video_result["snippet"]["channelTitle"],
                        "https://www.youtube.com/channel/"
                        + search_video_result["snippet"]["channelId"],
                        search_video_result["snippet"]["title"],
                        search_video_result["snippet"]["description"],
                        search_video_result["id"],
                        iso_to_jstdt(
                            search_video_result["liveStreamingDetails"]["actualStartTime"]
                        ),
                        int(
                            # search_video_result["liveStreamingDetails"]["concurrentViewers"]
                            search_video_result.get("liveStreamingDetails", {}).get("concurrentViewers", 0)
                        ),
                    ],
                    live_columns,
                )
                live_df = live_df.append(se, ignore_index=True)
        # 視聴者数が多い順にソート
        sorted_df = live_df.sort_values(["concurrentViewers"], ascending=False)

        context = {"sorted_df": sorted_df}

        return context


def iso_to_jstdt(iso_str: str) -> Optional[datetime]:
    """ISO時間（文字列）を日本時間（datetime型）に変換

    Args:
        iso_str (str):ISO時間

    Returns:
        str: 日本時間
    """
    dt = None
    try:
        dt = datetime.strptime(iso_str, "%Y-%m-%dT%H:%M:%S.%fZ")
        dt = pytz.utc.localize(dt).astimezone(pytz.timezone("Asia/Tokyo"))
    except ValueError:
        try:
            dt = datetime.strptime(iso_str, "%Y-%m-%dT%H:%M:%S.%f%z")
            dt = dt.astimezone(pytz.timezone("Asia/Tokyo"))
        except ValueError:
            pass
    return dt


class RetrieveYoutubeComment(TemplateView):
    """Youtubeコメントを取得"""

    template_name = "youtube_comment.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        form = VideoIdForm(self.request.GET or None)
        if form.is_valid():
            # 入力フォームからkeyword,display_number取得
            video_id = form.cleaned_data.get("video_id")
            display_number = int(form.cleaned_data.get("display_number"))
        context["form"] = form

        try:
            # 動画IDからコメント取得
            comment_df = retrieve_video_commnet(video_id, display_number)
            # 高評価数で降順
            comment_df = comment_df.sort_values(["like_cnt"], ascending=False)
            context = {
                "form": VideoIdForm(),  # フォーム初期化
                "comment_df": comment_df,
            }
            return context

        except:
            return context


def retrieve_video_commnet(video_id: str, comment_cnt: int) -> pd.DataFrame:
    """YouTube動画IDからコメントを取得する

    Args:
        video_id (str): Youtube動画ID
        comment_cnt (int): 取得コメント数

    Returns:
        pd.DataFrame: 取得したコメント情報のDataFrame
    """
    YOUTUBE_URL = "https://www.googleapis.com/youtube/v3/"
    params = {
        "key": YOUTUBE_API_KEY,
        "part": "snippet",
        "videoId": video_id,
        "order": "relevance",
        "textFormat": "plaintext",
        "maxResults": comment_cnt,
    }

    response = requests.get(YOUTUBE_URL + "commentThreads", params=params)
    resource = response.json()

    comment_list: list[str] = []
    for comment_info in resource["items"]:
        comment = {
            # コメント
            "text": comment_info["snippet"]["topLevelComment"]["snippet"][
                "textDisplay"
            ],
            # グッド数
            "like_cnt": comment_info["snippet"]["topLevelComment"]["snippet"][
                "likeCount"
            ],
            # 返信数
            "reply_cnt": comment_info["snippet"]["totalReplyCount"],
        }
        comment_list.append(comment)

    comment_df = pd.DataFrame(comment_list)
    return comment_df


class AllliveRanking(TemplateView):
    """ちくわちゃんランキング"""

    template_name = "all_live_ranking.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        ALL_LIVE_URL = "http://www.chikuwachan.com/twicas/"
        all_live_df = scrape_chikuwachan_ranking(ALL_LIVE_URL)
        context = {"all_live_df": all_live_df}
        logger.info("chikuwachan ranking: fullspec")
        return context


class YoutubeRanking(TemplateView):
    """Youtube by ちくわちゃんランキング"""

    template_name = "youtube_ranking.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        YOUTUBE_LIVE_URL = "http://www.chikuwachan.com/live/TUB/"
        youtube_live_df = scrape_chikuwachan_ranking(YOUTUBE_LIVE_URL)
        context = {"youtube_live_df": youtube_live_df}
        logger.info("chikuwachan ranking: Youtube")
        return context


class TwicasRanking(TemplateView):
    """Twicas by ちくわちゃんランキング"""

    template_name = "twicas_ranking.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        TWICAS_LIVE_URL = "http://www.chikuwachan.com/live/CAS/"
        twicas_live_df = scrape_chikuwachan_ranking(TWICAS_LIVE_URL)
        context = {"twicas_live_df": twicas_live_df}
        logger.info("chikuwachan ranking: Twicas")
        return context


class TwitchRanking(TemplateView):
    """Twitch by ちくわちゃんランキング"""

    template_name = "twitch_ranking.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        TWITCH_LIVE_URL = "http://www.chikuwachan.com/live/TCH/"
        twitch_live_df = scrape_chikuwachan_ranking(TWITCH_LIVE_URL)
        context = {"twitch_live_df": twitch_live_df}
        logger.info("chikuwachan ranking: Twitch")
        return context


def scrape_chikuwachan_ranking(URL: str) -> pd.DataFrame:
    """ちくわちゃんランキングから生放送情報をスクレイピングする

    Args:
        URL (str): スクレイピング対象URL

    Returns:
        pd.DataFrame: pandasのDataFrame型でスクレイピング情報を返却
    """
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    driver.get(URL)
    html = driver.page_source

    soup = BeautifulSoup(html, "lxml")
    live_list: list[str] = []
    for i in range(1, 26):
        common_selector = f"#ranking > div > ul > li:nth-child({i}) > "
        title_selector = common_selector + "div.content > a.liveurl > div.title"
        topic_selector = common_selector + "div.content > a.liveurl > div.topic"
        href_selector = common_selector + "div.content > a.liveurl"
        icon_selector = (
            common_selector + "div.content > a.liveurl > div.image_user > img"
        )
        image_selector = common_selector + "a > span > img"
        site_selector = common_selector + "div.content > a.siteicon > img"
        viewers_selector = common_selector + "div > div.count"
        progress_selector = common_selector + "div.content > div.progress"

        if i < 11:
            "10位以下と以上で要素が異なるため"
            live = {
                # 'title': driver.find_element_by_css_selector(title_selector).text,
                # 'topic': driver.find_element_by_css_selector(topic_selector).text,
                # 'url': driver.find_element_by_css_selector(href_selector).get_attribute('href'),
                # 'icon': driver.find_element_by_css_selector(icon_selector).get_attribute('src'),
                # 'image': driver.find_element_by_css_selector(image_selector).get_attribute('src'),
                # 'site': driver.find_element_by_css_selector(site_selector).get_attribute('src')
                "title": soup.select_one(title_selector).get_text(),
                "topic": soup.select_one(topic_selector).get_text(),
                "url": soup.select_one(href_selector).get("href"),
                "image": soup.select_one(image_selector).get("src"),
                "icon": soup.select_one(icon_selector).get("src"),
                "site": soup.select_one(site_selector).get("src"),
                "viewers": soup.select_one(viewers_selector).get_text(),
                "progress": soup.select_one(progress_selector).get_text(),
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
                "title": soup.select_one(title_selector).get_text(),
                "topic": soup.select_one(topic_selector).get_text(),
                "url": soup.select_one(href_selector).get("href"),
                "image": soup.select_one(image_selector).get("data-src"),
                "icon": soup.select_one(icon_selector).get("data-src"),
                "site": soup.select_one(site_selector).get("src"),
                "viewers": soup.select_one(viewers_selector).get_text(),
                "progress": soup.select_one(progress_selector).get_text(),
            }
            live_list.append(live)
    live_df = pd.DataFrame(live_list)
    logger.info("scraping completed")
    return live_df


class pornConfirm(TemplateView):
    template_name = "porn_confirm.html"


class PornhubRanking(TemplateView):
    """Pornhubランキング"""

    template_name = "pornhub_ranking.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        video_list_df = get_pornhub(26)
        context = {"video_list_df": video_list_df}
        return context


def get_pornhub(count: int) -> pd.DataFrame:
    """PornHUB APIからビデオ情報を取得する

    Args:
        count (int): 取得件数

    Returns:
        pd.DataFrame: API取得したビデオ情報を返却
    """
    from pornhub_api import PornhubApi
    from pornhub_api.backends.aiohttp import AioHttpBackend

    api = PornhubApi()
    category = "japanese"
    data = api.search.search(
        # "japanese",
        period="day",
        category=[category]
        # tags=["japanese"],
        # ordering="rating"
    )
    THUMBNAIL_URL = "https://ci.phncdn.com/"
    video_list: list[str] = []
    for video in data.videos[:count]:
        data = {
            "title": video.title,
            "publish_date": video.publish_date,
            "views": video.views,
            "rating": float(video.rating),
            "duration": video.duration,
            "url": "https://www.pornhub.com/view_video.php?" + video.url.query,
            "image1": THUMBNAIL_URL + video.thumbs[0].src.path,
            "image2": THUMBNAIL_URL + video.thumbs[2].src.path,
            "image3": THUMBNAIL_URL + video.thumbs[4].src.path,
            "image4": THUMBNAIL_URL + video.thumbs[6].src.path,
            "image5": THUMBNAIL_URL + video.thumbs[8].src.path,
            "image6": THUMBNAIL_URL + video.thumbs[10].src.path,
            "image7": THUMBNAIL_URL + video.thumbs[12].src.path,
            "image8": THUMBNAIL_URL + video.thumbs[14].src.path,
        }
        video_list.append(data)
    video_list_df = pd.DataFrame(video_list)  # 辞書のリストからDF生成
    video_list_df = video_list_df.sort_values(["rating", "views"], ascending=False)
    logger.info(f"pornhub video category: {category}")
    return video_list_df


class FanzaRanking(TemplateView):
    """Fanzaランキング"""

    template_name = "fanza_ranking.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        video_list_df = get_fanza(10)
        context = {"video_list_df": video_list_df}
        return context


def get_fanza(count: int) -> pd.DataFrame:
    """Fanza APIからビデオ情報を取得する

    Args:
        count (int): 取得件数

    Returns:
        pd.DataFrame: API取得したビデオ情報を返却
    """
    import dmm
    import datetime

    api_id = settings.FANZA_API_ID
    affiliate_id = settings.FANZA_AFFILIATE_ID

    # インスタンスを作成
    api = dmm.API(api_id=api_id, affiliate_id=affiliate_id)

    now = datetime.datetime.now()
    av_list: list[str] = []
    items = api.item_search(site="FANZA", service="digital", lte_date=now.strftime("%Y-%m-%dT%H:%M:%S"), hits=count)
    for i in items["result"]["items"]:
        av_dict = {
            "content_id": i["content_id"],
            "title": i["title"],
            "date": i["date"],
            "affiliateURL": i["affiliateURL"],
            "sampleMovieURL": i.get("sampleMovieURL", {}).get("size_644_414", None),
            "review_average": float(i.get('review', {}).get('average', 0)),
            "review_count": int(i.get('review', {}).get('count', 0))
        }
        av_list.append(av_dict)
    av_df = pd.DataFrame(av_list)
    av_sorted_df = av_df.sort_values(by=["review_count", "review_average"], ascending=False)
    return av_sorted_df
