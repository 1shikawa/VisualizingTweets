from django.urls import path
from . import views

app_name = 'VisualizingTweets'

urlpatterns = [
    path('', views.Index.as_view(), name='Index'),
    path('keywordSearch/', views.KeyWordSearch.as_view(), name='keyword_search'),
    path('stock/<str:screen_name>/status/<int:tweet_id>', views.StockAdd.as_view(), name='stock_add'),
    path('stockList/', views.StockList.as_view(), name='stock_list'),
    path('stockUpdate/<int:pk>', views.StockUpdate.as_view(), name='stock_update'),
    path('stockDelete/<int:pk>', views.StockDelete.as_view(), name='stock_delete'),
    ]
