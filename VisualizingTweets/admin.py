from dataclasses import fields
import resource
from django.contrib import admin
from import_export import resources
from import_export.admin import ExportActionMixin
from .models import Stock


class StockResource(resources.ModelResource):
    class Meta:
        model = Stock
        fields = export_order = ['tweet_id', 'user_id', 'screen_name', 'user_name', 'tweet_created_at',
                                 'tweet_text', 'expanded_url', 'created_at', 'stock_user']
# Register your models here.


class StockAdmin(ExportActionMixin, admin.ModelAdmin):
    resource_class = StockResource
    actions = ['export_admin_action']
    list_display = ['tweet_id', 'user_id', 'screen_name', 'user_name', 'tweet_created_at',
                    'tweet_text', 'expanded_url', 'created_at', 'stock_user']
    list_display_links = ('tweet_id',)
    list_editable = ()


admin.site.register(Stock, StockAdmin)
# tweet_url = models.URLField('ツイートURL', max_length=300, blank=True)
# tweet_created_at = models.DateField('ツイート日', blank=True)
# favorite_count = models.PositiveIntegerField('いいね数', blank=True, default=0)
# retweet_count = models.PositiveIntegerField(
#     'リツイート数', blank=True, default=0)
# expanded_url = models.URLField(
#     '関連URL', max_length=300, blank=True, default='http://example.com')
# created_at = models.DateTimeField(auto_now_add=True)
