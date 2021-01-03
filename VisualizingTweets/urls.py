from django.urls import path
from . import views

app_name = 'VisualizingTweets'

urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    path('timelineSearch/', views.timelineSearch.as_view(), name='timeline_search'),
    path('keywordSearch/', views.KeyWordSearch.as_view(), name='keyword_search'),
    path('FollowUsers/', views.FollowUsers.as_view(), name='follow_users'),
    path('SpecifiedUrl/', views.SpecifiedUrl.as_view(), name='specified_url'),
    path('CreateStock/<str:tweet_id>', views.create_stock, name='create_stock'),
    path('Stock/<str:screen_name>/status/<int:tweet_id>', views.StockAdd.as_view(), name='stock_add'),
    path('StockList/', views.StockList.as_view(), name='stock_list'),
    path('StockUpdate/<int:pk>', views.StockUpdate.as_view(), name='stock_update'),
    path('StockDelete/<int:pk>', views.StockDelete.as_view(), name='stock_delete'),
    ]
