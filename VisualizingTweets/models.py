from django.db import models
from django.urls import reverse_lazy


class Stock(models.Model):
    tweet_id = models.CharField('ツイートID', max_length=50, blank=True, null=True)
    user_id = models.CharField('ユーザーID', max_length=50, blank=True, null=True)
    screen_name = models.CharField('スクリーン名', max_length=100, blank=True, null=True)
    user_name = models.CharField('ユーザー名', max_length=100, blank=True, null=True)
    tweet_text = models.TextField('ツイート内容', max_length=500, blank=True, null=True)
    tweet_url = models.URLField('ツイートURL', max_length=300, blank=True, null=True)
    tweet_created_at = models.DateTimeField('ツイート日', blank=True, null=True)
    favorite_count = models.PositiveIntegerField('いいね数', blank=True, default=0)
    retweet_count = models.PositiveIntegerField('リツイート数', blank=True,default=0)
    expanded_url = models.URLField('関連URL', max_length=300, blank=True,default='http://example.com')
    created_at = models.DateTimeField('ストック日', auto_now_add=True, null=True)
    stock_user = models.CharField('ストック者', max_length=30, blank=True, null=True)
    updated_at = models.DateTimeField('更新日', auto_now=True, null=True)

    def get_absolute_url(self):
        return reverse_lazy("VisualizingTweets:stock_add", kwargs={
            'screen_name': self.screen_name,
            'tweet_id': self.tweet_id
         })

    def __str__(self):
        return str(self.tweet_id)
