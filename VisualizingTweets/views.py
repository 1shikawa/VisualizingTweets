from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView
from django.http import Http404, HttpResponse
from django.conf import settings
from .models import Stock
from .forms import SearchForm, KeyWordSearchForm, StockCreateForm, StockUpdateForm
import requests
import logging
import pandas as pd
import tweepy
import pprint

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
                    return redirect('Visualizing:timeline_search', form)

                # Tweepy,Statusオブジェクトからツイート情報取得
                for tweet in tweepy.Cursor(api.user_timeline, screen_name=screen_name, exclude_replies=True, trim_user=True, include_entities=True, include_rts=False).items(display_number):
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
                                URL + screen_name + '/status/'+ tweet.id_str  # ツイートリンクURL
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
                return context
        except:
            # messages.error(self.request, 'エラーが発生しました。')
            return context


# dataframeのカラム定義
columns2 = [
    'screen_name',
    'user_name',
    'tweet_id',
    'created_at',
    'text',
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
        tweets_df = pd.DataFrame(columns=columns2)

        try:
            print(lang)
            for tweet in tweepy.Cursor(api.search, q=keyword, lang=lang, include_entities=True, include_rts=False).items(display_number):
                if not tweet.text.startswith('RT @'):
                    se = pd.Series([
                        # ツイート情報
                        tweet.user.screen_name,
                        tweet.user.name,
                        tweet.id,
                        tweet.created_at,
                        tweet.text,
                        tweet.favorite_count,
                        tweet.retweet_count,
                        URL + tweet.user.screen_name + '/status/' + tweet.id_str,  # ツイートリンクURL
                        # ツイートしたユーザー情報
                        tweet.user.profile_image_url,
                        tweet.user.statuses_count,
                        tweet.user.followers_count,
                    ], columns2
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
            # pprint.pprint(tweets_df)
            return context
        except:
            return context


class StockList(LoginRequiredMixin, ListView):
    model = Stock
    template_name = 'stock_list.html'
    context_object_name = 'stock_list'

    def get_queryset(self):
        queryset = Stock.objects.filter(stock_user=self.request.user)
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
        # tweet_idからツイート情報取得
        tweet = api.get_status(id=tweet_id)
        if tweet.entities['urls']:
            expanded_url = tweet.entities['urls'][0]['expanded_url']
        else:
            expanded_url = ''
        form = StockCreateForm(
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
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'ストックの更新に失敗しました。')
        return super().form_invalid(form)


class StockDelete(LoginRequiredMixin, DeleteView):
    model = Stock
    success_url = reverse_lazy('VisualizingTweets:stock_list')

    # 確認画面を省略するためにgetをpostにショートカット
    def get(self, *args, **kwargs):
        messages.success(self.request, '対象ストックを削除しました。')
        return self.post(*args, **kwargs)


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
