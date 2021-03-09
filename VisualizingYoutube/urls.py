from django.urls import path
from . import views

app_name = 'VisualizingYoutube'

urlpatterns = [
    path('videoSearch/', views.videoSearch.as_view(), name='video_search'),
    path('YoutubeLiveRanking/', views.YoutubeLiveRanking.as_view(), name='youtubelive_ranking'),
    path('YoutubeRetrieveComment/', views.RetrieveYoutubeComment.as_view(), name='youtube_comment'),
    path('pornConfirm/', views.pornConfirm.as_view(), name='porn_confirm'),
    path('pornhubRanking/', views.PornhubRanking.as_view(), name='pornhub_ranking'),
    path('AllliveRanking/', views.AllliveRanking.as_view(), name='all_live_ranking'),
    path('YoutubeRanking/', views.YoutubeRanking.as_view(), name='youtube_ranking'),
    path('TwicasRanking/', views.TwicasRanking.as_view(), name='twicas_ranking'),
    path('TwitchRanking/', views.TwitchRanking.as_view(), name='twitch_ranking'),
    path('fanzaRanking/', views.FanzaRanking.as_view(), name='fanza_ranking')
]
