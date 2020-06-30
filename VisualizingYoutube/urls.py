from django.urls import path
from . import views

app_name = 'VisualizingYoutube'

urlpatterns = [
    path('videoSearch/', views.videoSearch.as_view(), name='video_search'),
    path('liveRanking/', views.liveRanking.as_view(), name='live_ranking'),
    path('AllliveRanking/', views.AllliveRanking.as_view(), name='all_live_ranking'),
]
