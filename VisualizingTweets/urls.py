from django.urls import path
from . import views

app_name = 'VisualizingTweets'

urlpatterns = [
    path('', views.Index.as_view(), name='Index'),
    path('Stock/<str:screen_name>/<str:tweet_id>', views.StockAdd.as_view(), name='stock_add'),
    path('StockList/', views.StockList.as_view(), name='stock_list'),
    ]
