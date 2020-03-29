from django.urls import path
from . import views

app_name = 'VisualizingTweets'

urlpatterns = [
    path('index/', views.Index.as_view(), name='Index'),
    ]
