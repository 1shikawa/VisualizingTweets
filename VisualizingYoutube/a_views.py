from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView
from django.http import Http404, HttpResponse
from django.conf import settings
# from .forms import LiveSearchForm
import http.client
import httplib2
import requests
import os
import logging
import pandas as pd
import pprint

from apiclient.discovery import build
from apiclient.errors import HttpError
from apiclient.http import MediaFileUpload
from oauth2client import tools
from oauth2client import client
from oauth2client.file import Storage
# YouTubeAPI OAuthの各種設定
httplib2.RETRIES = 1
MAX_RETRIES = 10
RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError,
                        )
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]
# CLIENT_SECRETS_FILE = "/code/VisualizingYoutube/credentials/client_secrets.json"
CLIENT_SECRETS_FILE = "/code/VisualizingYoutube/client_secrets.json"
MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:

   %s

with information from the API Console
https://console.developers.google.com/

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % os.path.abspath(os.path.join(os.path.dirname(__file__),
                                   CLIENT_SECRETS_FILE))

YOUTUBE_SCOPE = "https://www.googleapis.com/auth/youtube"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# dataframeのカラム定義
columns = [
    'videoId',
    'title',
    'thumbnails',
    'url'
]


class Index(TemplateView):
    template_name = 'live_list.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        # Youtubeインスタンス作成

        credentials_path = "credentials.json"
        if os.path.exists(credentials_path):
            # 認証済み
            store = Storage(credentials_path)
            credentials = store.get()
        else:
            # 認証処理
            f = "/code/VisualizingYoutube/client.json"
            scope = "https://www.googleapis.com/auth/youtube.readonly"
            flow = client.flow_from_clientsecrets(f, scope)
            flow.user_agent = "YouTubeLiveStreaming"
            credentials = tools.run_flow(flow, Storage(credentials_path))

        # search_response = youtube.search().list(
        #     # q='ThtcrBgB4KY',
        #     regionCode='JP',
        #     eventType='live',
        #     type='video',
        #     part='id,snippet',
        #     order='viewCount',
        #     maxResults=10,
        # ).execute()

        # print(search_response)

        # context = {
        #     'sorted_df': sorted_df
        # }

        return context


def get_authenticated_service():
    flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
                                    scope=YOUTUBE_SCOPE,
                                    message=MISSING_CLIENT_SECRETS_MESSAGE)

    storage = Storage("/code/VisualizingYoutube/%s-oauth2.json" % 'liveStreaming')
    credentials = storage.get()
    # credentials = get_credentials()

    if credentials is None or credentials.invalid:
        credentials = run_flow(flow, storage)

    return build(YOUTUBE_API_SERVICE_NAME,
                 YOUTUBE_API_VERSION,
                 http=credentials.authorize(httplib2.Http()))

def get_credentials():
    script_dir = os.path.abspath(os.path.dirname(__file__))
    credential_dir = os.path.join(script_dir, '.credentials')

    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir, 'client_secrets.json')

    store = Storage(credential_path)
    credentials = store.get()
    return credentials
