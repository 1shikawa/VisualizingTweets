from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from django.views.generic import TemplateView, ListView, CreateView
from django.http import Http404, HttpResponse
from django.conf import settings
from .models import Stock
from .forms import SearchForm, StockForm
import requests
import logging
import pandas as pd
import tweepy

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
URL = 'https://twitter.com/'

# デフォルトツイート取得件数
default_display_number = 300

# dataframeのカラム定義
columns = [
    'screen_name',
    'tweet_id',
    'created_at',
    'text',
    'fav',
    'retweets',
    'url'
]


class Index(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        form = SearchForm(self.request.GET or None, initial={'display_number': default_display_number})
        if form.is_valid():
            # 入力フォームからuser_idとdisplay_number取得
            screen_name = form.cleaned_data.get('screen_name')
            display_number = int(form.cleaned_data.get('display_number'))
        context['form'] = form
        # columns定義したDataFrameを作成
        tweets_df = pd.DataFrame(columns=columns)
        try:
            if screen_name and display_number:
                # 対象ユーザーが存在するかどうか確認
                res = requests.get(URL + screen_name)
                if res.status_code == 200:
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
                    return redirect('Visualizing:Index', form)

                # Tweepy,Statusオブジェクトからツイート情報取得
                for tweet in tweepy.Cursor(api.user_timeline, screen_name=screen_name, exclude_replies=True, include_entities=True, include_rts=False).items(display_number):
                    try:
                        if not "RT @" in tweet.text and tweet.favorite_count != 0:
                            se = pd.Series([
                                screen_name,
                                tweet.id,
                                tweet.created_at,
                                # tweet.text.replace('\n', ''),
                                tweet.text,
                                tweet.favorite_count,
                                tweet.retweet_count,
                                URL+screen_name + '/status/'+tweet.id_str  # ツイートリンクURL
                            ], columns
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
                # リツイート＆いいね数が多い順にソート
                sorted_df = tweets_df.sort_values(['fav', 'retweets'], ascending=False)
                # created_atをキーに昇順ソート
                sorted_df_created_at = tweets_df.sort_values('created_at', ascending=True)
                # チャート縦軸調整のためのfav最大数取得
                sorted_df_MaxFav = max(sorted_df['fav'])

                context = {
                    'form': SearchForm(initial={'display_number': default_display_number}), # フォーム初期化
                    'screen_name': screen_name,
                    'tweets_df': tweets_df,
                    'grouped_df': grouped_df,
                    'sorted_df': sorted_df,
                    'sorted_df_MaxFav': sorted_df_MaxFav,
                    'sorted_df_created_at' : sorted_df_created_at,
                    'profile': profile,
                    'display_number': display_number,
                }

                return context

        except:
            # messages.error(self.request, 'エラーが発生しました。')
            return context


# def Stock(request, tweet_id):
#     tweet = api.get_status(id=tweet_id)
#     return HttpResponse(f'ツイートIDは{tweet}です。')

class StockList(ListView):
    model = Stock
    template_name = 'stock_list.html'
    context_object_name = 'stock_list'

class StockAdd(CreateView):
    model = Stock
    template_name = 'stock_add.html'
    form_class = StockForm
    # success_url = reverse_lazy('VisualizingTweets:Index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tweet_id = self.kwargs['tweet_id']
        if Stock.objects.filter(tweet_id=tweet_id).exists():
            messages.warning(self.request, '既にストック済みです。')

        tweet = api.get_status(id=tweet_id)
        if tweet.entities['urls']:
            expanded_url = tweet.entities['urls'][0]['expanded_url']
        else:
            expanded_url = ''
        form = StockForm(
            initial={'tweet_id': tweet_id,
                     'user_id': tweet.user.id_str,
                     'screen_name': tweet.user.screen_name,
                     'user_name': tweet.user.name,
                     'tweet_text': tweet.text,
                     'tweet_url': URL + tweet.user.id_str + '/status/' + tweet.id_str,
                     'tweet_created_at': tweet.created_at,
                     'favorite_count': tweet.favorite_count,
                     'retweet_count': tweet.retweet_count,
                     'expanded_url': expanded_url
                     })
        context['form'] = form
        return context

    def post(self, request, *args, **kwargs):
        messages.success(self.request, 'ストックしました。')
        return super().post(request, *args, **kwargs)


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
