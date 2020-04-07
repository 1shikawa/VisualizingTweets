from django.urls import path
from . import views

app_name = 'VisualizingTweets'

urlpatterns = [
    path('', views.Index.as_view(), name='Index'),
    path('Stock/<str:tweet_id>', views.StockCreateView.as_view(), name='Stock'),
    ]
