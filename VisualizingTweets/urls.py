from django.urls import path
from . import views

app_name = 'VisualizingTweets'

urlpatterns = [
    path('', views.Index.as_view(), name='Index'),
    path('KeywordSearch/', views.KeyWordSearch.as_view(), name='keyword_search'),
    path('Stock/<str:screen_name>/<int:tweet_id>', views.StockAdd.as_view(), name='stock_add'),
    path('StockList/', views.StockList.as_view(), name='stock_list'),
    path('StockUpdate/<int:pk>', views.StockUpdate.as_view(), name='stock_update'),
    path('StockDelete/<int:pk>', views.StockDelete.as_view(), name='stock_delete'),
    ]
