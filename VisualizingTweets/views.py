from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView
from django.http import Http404, HttpResponse
from django.conf import settings
from .models import Stock
from .forms import SearchForm, KeyWordSearchForm, StockCreateForm, StockUpdateForm, SpecifiedUrlForm
import requests
import concurrent.futures
import logging
import pandas as pd
import tweepy
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# 各種Twitterーのキーをセット
CONSUMER_KEY = settings.CONSUMER_KEY
CONSUMER_SECRET = settings.CONSUMER_SECRET
ACCESS_TOKEN = settings.ACCESS_TOKEN
ACCESS_TOKEN_SECRET = settings.ACCESS_TOKEN_SECRET

# Tweepy
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

# APIインスタンスを作成
api = tweepy.API(auth)

# Twitter URL
TWITTER_URL = 'https://twitter.com/'

# dataframeのカラム定義
twitter_trend_columns = [
    'name',
    'tweet_volume',
    'url'
]

yahoo_comment_columns = [
    'rank',
    'title',
    'time',
    'comment_volume',
    'url'
]

class Index(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        # pprint.pprint(api.trends_available())
        jp_area_code = '23424856'
        us_area_code = '23424977'

        # concurrent.futuresによるマルチスレッド処理
        with concurrent.futures.ThreadPoolExecutor(max_workers=3, thread_name_prefix='thread') as executor:
            jp_twitter_trend = executor.submit(get_twitter_trend_df, jp_area_code)
            us_twitter_trend = executor.submit(get_twitter_trend_df, us_area_code)
            yahoo_news = executor.submit(scraping_yahoo_news)
        # logger.info(jp_twitter_trend_df)
        context = {
            'jp_twitter_trend_df': jp_twitter_trend.result(),
            'us_twitter_trend_df': us_twitter_trend.result(),
            'yahoo_news_df': yahoo_news.result(),
        }
        logger.info('Twitter trend and Yahoo news scraping completed')
        return context


def scraping_yahoo_news() -> pd.DataFrame:
    # Yahooニュースコメントランキングからスクレイピング
    YAHOO_NEWS_URL = 'https://news.yahoo.co.jp/ranking/comment'
    html = requests.get(YAHOO_NEWS_URL)
    soup = BeautifulSoup(html.text, "html.parser")
    topicsindex = soup.find('div', attrs={'class': 'newsFeed'})
    topics = topicsindex.find_all('li')

    # columns定義したDataFrameを作成
    yahoo_news_df = pd.DataFrame(columns=yahoo_comment_columns)
    for topic in topics:
        se = pd.Series([
            topic.find('span', attrs={
                        'class': 'newsFeed_item_rankNum'}).contents[0],
            topic.find('div', attrs={
                        'class': 'newsFeed_item_title'}).contents[0],
            topic.find('time', attrs={
                        'class': 'newsFeed_item_date'}).contents[0],
            int(topic.find('em').contents[0]),
            topic.find('a').get('href')
        ], yahoo_comment_columns
        )
        yahoo_news_df = yahoo_news_df.append(se, ignore_index=True)

    return yahoo_news_df


def get_twitter_trend_df(parentid: str) -> pd.DataFrame:
    """parentidから各国のTwitterトレンドを取得
    arument: 地域コード
    return: DataFrame
    """
    trends = api.trends_place(parentid)
    # # columns定義したDataFrameを作成
    twitter_trend_df = pd.DataFrame(columns=twitter_trend_columns)
    for trend in trends[0]['trends']:
        se = pd.Series([
            trend['name'],
            trend['tweet_volume'],
            trend['url']
        ], twitter_trend_columns
        )
        twitter_trend_df = twitter_trend_df.append(se, ignore_index=True)
    twitter_trend_df = twitter_trend_df.dropna(subset=['tweet_volume'])
    # twitter_trend_df = twitter_trend_df.fillna(0)
    twitter_trend_df = twitter_trend_df.sort_values(['tweet_volume'], ascending=False)

    return twitter_trend_df


# dataframeのカラム定義
timeline_columns = [
    'screen_name',
    'tweet_id',
    'created_at',
    'full_text',
    'fav',
    'retweets',
    'tweet_url',
    # 'media_url'
]
class timelineSearch(TemplateView):
    template_name = 'timeline_search.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        form = SearchForm(self.request.GET or None)
        if form.is_valid():
            # 入力フォームからscreen_nameとdisplay_number取得
            screen_name = form.cleaned_data.get('screen_name')
            display_number = int(form.cleaned_data.get('display_number'))
        context['form'] = form
        # columns定義したDataFrameを作成
        tweets_df = pd.DataFrame(columns=timeline_columns)
        try:
            if screen_name and display_number:
                # 対象ユーザーが存在するかどうか確認
                res = requests.get(TWITTER_URL + screen_name)
                if res.status_code:
                    # Userオブジェクトからプロフィール情報取得
                    user = api.get_user(screen_name=screen_name)
                    profile = {
                        'id': user.id,
                        'screen_name': user.screen_name,
                        'user_name': user.name,
                        'statuses_count': user.statuses_count,
                        'followers_count': user.followers_count,
                        'created_at': user.created_at,
                        'image': user.profile_image_url,
                        'description': user.description
                    }
                    messages.success(self.request, f'{screen_name}のツイート情報を表示します。')

                else:
                    messages.warning(self.request, f'{screen_name}が見つかりません。')
                    form = SearchForm()
                    return redirect('Visualizing:timeline_search', form)

                # Tweepy,Statusオブジェクトからツイート情報取得
                for tweet in tweepy.Cursor(api.user_timeline, screen_name=screen_name, exclude_replies=True, trim_user=True, include_entities=True, include_rts=False, result_type="mixed", tweet_mode="extended").items(display_number):
                    try:
                        if not "RT @" in tweet.full_text and tweet.favorite_count != 0:
                            se = pd.Series([
                                screen_name,
                                tweet.id,
                                tweet.created_at,
                                # tweet.text.replace('\n', ''),
                                tweet.full_text,
                                int(tweet.favorite_count),
                                int(tweet.retweet_count),
                                TWITTER_URL + screen_name + '/status/' + tweet.id_str, # ツイートリンクURL
                                # tweet.entities['media'][0]['media_url'] if tweet.entities['media'] else tweet.id,
                                ], timeline_columns
                            )
                        tweets_df = tweets_df.append(se, ignore_index=True)

                    except Exception as e:
                        print(e)

                # created_atを日付型に変換
                tweets_df['created_at'] = pd.to_datetime(tweets_df['created_at'])
                # 重複するツイートを削除
                tweets_df = tweets_df.drop_duplicates(subset='tweet_id')
                # 日別のリツイート、いいね数の合計
                grouped_df = tweets_df.groupby(tweets_df.created_at.dt.date).sum().sort_values(by='created_at',
                                                                                            ascending=False)
                # いいね,リツイート数が多い順にソート
                sorted_df = tweets_df.sort_values(['fav', 'retweets'], ascending=False)
                # created_atをキーに昇順ソート
                sorted_df_created_at = tweets_df.sort_values('created_at', ascending=True)
                # チャート縦軸調整のためのfav最大数取得
                sorted_df_MaxFav = max(sorted_df['fav'])

                context = {
                    'form': SearchForm(), # フォーム初期化
                    'screen_name': screen_name,
                    'tweets_df': tweets_df,
                    'grouped_df': grouped_df,
                    'sorted_df': sorted_df,
                    'sorted_df_MaxFav': sorted_df_MaxFav,
                    'sorted_df_created_at' : sorted_df_created_at,
                    'profile': profile,
                    'display_number': display_number,
                }
                logging.info(f'screen_name: {screen_name} timeline is OK')
                return context
        except:
            # messages.error(self.request, 'エラーが発生しました。')
            return context


# dataframeのカラム定義
keysearch_columns = [
    'screen_name',
    'user_name',
    'tweet_id',
    'created_at',
    'full_text',
    'fav',
    'retweets',
    'url',
    'user_image',
    'statuses_count',
    'followers_count'
]
class KeyWordSearch(TemplateView):
    template_name = 'keyword_search.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        form = KeyWordSearchForm(self.request.GET or None)
        if form.is_valid():
            keyword = form.cleaned_data.get('keyword')
            display_number = int(form.cleaned_data.get('display_number'))
            lang = form.cleaned_data.get('lang')
        context['form'] = form

        # columns定義したDataFrameを作成
        tweets_df = pd.DataFrame(columns=keysearch_columns)

        try:
            for tweet in tweepy.Cursor(api.search, q=keyword, lang=lang, include_entities=True, include_rts=False, result_type="mixed", tweet_mode="extended").items(display_number):
                if not tweet.full_text.startswith('RT @'):
                    se = pd.Series([
                        # ツイート情報
                        tweet.user.screen_name,
                        tweet.user.name,
                        tweet.id,
                        tweet.created_at,
                        tweet.full_text,
                        int(tweet.favorite_count),
                        int(tweet.retweet_count),
                        TWITTER_URL + tweet.user.screen_name + '/status/' + tweet.id_str,  # ツイートリンクURL
                        # ツイートしたユーザー情報
                        tweet.user.profile_image_url,
                        tweet.user.statuses_count,
                        tweet.user.followers_count,
                    ], keysearch_columns
                    )
                    tweets_df = tweets_df.append(se, ignore_index=True)
            # 重複するツイートを削除
            tweets_df = tweets_df.drop_duplicates(subset='tweet_id')
            # いいね,リツイート数が多い順にソート
            sorted_df = tweets_df.sort_values(['fav', 'retweets'], ascending=False)

            context = {
                'form': KeyWordSearchForm(), # フォーム初期化
                'sorted_df': sorted_df,
                'display_number': display_number
            }
            logging.info(f'search keyword: {keyword} is OK')
            return context

        except:
            return context


class StockList(LoginRequiredMixin, ListView):
    model = Stock
    template_name = 'stock_list.html'
    context_object_name = 'stock_list'

    def get_queryset(self):
        queryset = Stock.objects.filter(stock_user=self.request.user)
        logging.info(f'display {self.request.user}\'s stock list')
        return queryset


class StockAdd(LoginRequiredMixin, CreateView):
    model = Stock
    form_class = StockCreateForm
    template_name = 'stock_add.html'
    # success_url = reverse_lazy('VisualizingTweets:Index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tweet_id = self.kwargs['tweet_id']
        if Stock.objects.filter(tweet_id=tweet_id, stock_user=str(self.request.user)).exists():
            messages.warning(self.request, '既にストック済みです。')
            logging.info(f'{tweet_id} has been saved')
        # tweet_idからツイート情報取得
        tweet = api.get_status(id=tweet_id, result_type="mixed", tweet_mode="extended")
        if tweet.entities['urls']:
            expanded_url = tweet.entities['urls'][0]['expanded_url']
        else:
            expanded_url = ''
        form = StockCreateForm(
            initial={'tweet_id': tweet_id,
                    'user_id': tweet.user.id_str,
                    'screen_name': tweet.user.screen_name,
                    'user_name': tweet.user.name,
                    'tweet_text': tweet.full_text,
                    'tweet_url': TWITTER_URL + tweet.user.id_str + '/status/' + tweet.id_str,
                    'tweet_created_at': tweet.created_at,
                    'favorite_count': tweet.favorite_count,
                    'retweet_count': tweet.retweet_count,
                    'expanded_url': expanded_url
                    })
        context['form'] = form
        return context

    def form_valid(self, form):
        stock = form.save(commit=False)
        stock.stock_user = str(self.request.user)
        stock.save()
        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        messages.success(self.request, 'ストックしました。')
        return super().post(request, *args, **kwargs)


class StockUpdate(LoginRequiredMixin, UpdateView):
    model = Stock
    form_class = StockUpdateForm
    template_name = 'stock_update.html'
    success_url = reverse_lazy('VisualizingTweets:stock_list')

    # def get_success_url(self):
    #     return reverse_lazy('VisualizingTweets:stock_update', kwargs={'pk': self.kwargs['pk']})

    def form_valid(self, form):
        stock = form.save()
        messages.success(self.request, f'ID：{stock.pk}のストックを更新しました。')
        logging.info(f'pk: {stock.pk} stock updated')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'ストックの更新に失敗しました。')
        logging.error(f'pk: {stock.pk} stock update failure')
        return super().form_invalid(form)


class StockDelete(LoginRequiredMixin, DeleteView):
    model = Stock
    success_url = reverse_lazy('VisualizingTweets:stock_list')

    # 確認画面を省略するためにgetをpostにショートカット
    def get(self, *args, **kwargs):
        messages.success(self.request, '対象ストックを削除しました。')
        logging.info(f'pk: {stock.pk} stock deleted')
        return self.post(*args, **kwargs)


class SpecifiedUrl(LoginRequiredMixin, TemplateView):
    template_name = 'specified_url.html'
    form_class = SpecifiedUrlForm

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        form = SpecifiedUrlForm(self.request.GET or None)
        if form.is_valid():
            tweet_url = form.cleaned_data.get('tweet_url')
        context['form'] = form

        try:
            tweet_id = get_tweet_id(tweet_url)

            if Stock.objects.filter(tweet_id=tweet_id, stock_user=str(self.request.user)).exists():
                messages.warning(self.request, '既にストック済みです。')
                logging.info(f'{tweet_id} stock has been saved')
                return context

            else:
                tweet = api.get_status(id=tweet_id, result_type="mixed", tweet_mode="extended")
                if tweet.entities['urls']:
                    expanded_url = tweet.entities['urls'][0]['expanded_url']
                else:
                    expanded_url = ''

                # if tweet.entities['media']:
                #     media_url = tweet.entities['media'][0]['media_url']
                # else:
                #     media_url = ''

                context ={
                    'form': SpecifiedUrlForm(),
                    'tweet_id': tweet_id,
                    'user_id': tweet.user.id_str,
                    'screen_name': tweet.user.screen_name,
                    'user_name': tweet.user.name,
                    'tweet_text': tweet.full_text,
                    'tweet_url': TWITTER_URL + tweet.user.id_str + '/status/' + tweet.id_str,
                    'tweet_created_at': tweet.created_at,
                    'favorite_count': tweet.favorite_count,
                    'retweet_count': tweet.retweet_count,
                    'expanded_url': expanded_url,
                    # 'media_url': media_url
                }
                return context
        except:
            return context


def get_tweet_id(url: str) -> str:
    """TweetURLからscreen_nameとstatus_idを取得
    argment: ツイッターURL
    return: ツイート固有ID(status)
    """
    url = url.replace('https://twitter.com/','')
    data = url.split('/')
    screen_name = data[0]
    tweet_id = int(data[2])
    return tweet_id


def create_stock(request, tweet_id):
    if request.method == 'POST':
        tweet = api.get_status(id=tweet_id, result_type="mixed", tweet_mode="extended")
        if tweet.entities['urls']:
            expanded_url = tweet.entities['urls'][0]['expanded_url']
        else:
            expanded_url = ''
        stock = Stock.objects.create(
            tweet_id = tweet.id,
            screen_name = tweet.user.screen_name,
            user_id =  tweet.user.id_str,
            user_name =  tweet.user.name,
            tweet_text =  tweet.full_text,
            tweet_url =  TWITTER_URL + tweet.user.id_str + '/status/' + tweet.id_str,
            tweet_created_at = tweet.created_at,
            favorite_count = tweet.favorite_count,
            retweet_count = tweet.retweet_count,
            expanded_url = expanded_url,
            stock_user = str(request.user)
        )
        stock.save()
        messages.success(request, 'ストックしました。')
        logging.info(f'tweet_id: {tweet_id} stocked')
        return redirect('VisualizingTweets:specified_url')
    else:
        return redirect('VisualizingTweets:specified_url')


# class BulkStockView(ListView):
#     template_name = 'BulkStock.html'
#     model = Stock

#     def post(self, request, *args, **kwargs):
#         checks_value = request.POST.getlist('tweets')
#         logger.debug("checks_value = " + str(checks_value))

# def BulkStockView(request):
#     checks_value = request.POST.getlist('tweets')
#     print("checks_value = " + str(checks_value))
#     return HttpResponse(checks_value)
