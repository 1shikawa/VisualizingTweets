from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, FormView
from django.http import Http404
from django.conf import settings
from .forms import SearchForm
import tweepy
import pandas as pd

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

# ツイート取得件数
display_number = 300

# Viewの処理
columns = [
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
        form = SearchForm(self.request.GET or None, initial={'display_number': display_number})
        if form.is_valid():
            # 入力フォームからuser_id取得
            user_id = form.cleaned_data.get('user_id')
            display_number = int(form.cleaned_data.get('display_number'))
        context['form'] = form
        # columns定義したDataFrameを作成
        tweets_df = pd.DataFrame(columns=columns)
        try:
            if user_id and display_number:
                # Tweepy,Statusオブジェクトから各値取得
                for tweet in tweepy.Cursor(api.user_timeline, screen_name=user_id, exclude_replies=True, include_entities=True, include_rts=False).items(display_number):
                    try:
                        if not "RT @" in tweet.text:
                            se = pd.Series([
                                tweet.id,
                                tweet.created_at,
                                tweet.text.replace('\n', ''),
                                tweet.favorite_count,
                                tweet.retweet_count,
                                URL+user_id +'/status/'+tweet.id_str #ツイートリンクURL
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
                ## sorted_df = tweets_df.groupby('tweet_id').sum('fav').sort_values(['retweets','fav'], ascending=False)
                # 縦軸調整のため最大のfav数取得
                sorted_df_MaxFav = max(sorted_df['fav'])

                # Userオブジェクトからプロフィール情報取得
                user = api.get_user(screen_name=user_id)
                profile = {
                    'id': user.id,
                    'user_id': user_id,
                    'user_name': user.name,
                    'statuses_count': user.statuses_count,
                    'followers_count': user.followers_count,
                    'created_at': user.created_at,
                    'image': user.profile_image_url,
                    'description': user.description
                }

                context = {
                    'form': form,
                    'user_id': user_id,
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
            context['message'] = 'エラーが発生しました。'
            return context

