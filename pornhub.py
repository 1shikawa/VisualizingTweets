import asyncio
from pornhub_api.backends.aiohttp import AioHttpBackend
from pornhub_api import PornhubApi
import pprint


# async def execute():
#     backend = AioHttpBackend()
#     api = PornhubApi(backend=backend)
#     response = await api.video.get_by_id("ph560b93077ddae")
#     print(response.video.title)

#     await backend.close()

# asyncio.run(execute())


# api = PornhubApi()
# data = api.search.search(
    # "chechick",
    # ordering="mostviewed",
    # period="day",
    # tags=["black"],
# )
# for vid in data.videos:
#     print(vid)
# pprint.pprint(data)

# video = api.video.get_by_id("ph58c466aa61bc5")
# print(video)
# video1 = api.video.get_by_id("ph58c466aa61bc5").video.title
# video2 = api.video.get_by_id("ph58c466aa61bc5").video.url.query
# pprint.pprint('https://www.pornhub.com/view_video.php?' + video2)
# video3 = api.video.get_by_id('ph58c466aa61bc5').video.thumbs[0].src.path
# pprint.pprint('https://ci.phncdn.com/' + video3)
# starts = api.stars.all()
# print(starts)

# categories = api.video.categories()
# print(categories)
# tags = api.video.tags("a")
# print(tags)



import tweepy
from bs4 import BeautifulSoup
import pprint
import time

# 各種Twitterーのキーをセット
CONSUMER_KEY = 'hvgtijJXhGaj2x8fyPVzjeZVG'
CONSUMER_SECRET = 'zuMm9DbQRKuMYyLVCmHbUjtV1OknXKWEusgh8kpgksrCchzws4'
ACCESS_TOKEN = '133257671-SlwXzmLBO5Xy1KYCsZyG4OSJf5QcEjZFV6gD3km2'
ACCESS_TOKEN_SECRET = 'zXdiZz6vpOkJn1G87LTredcCwO6vaUTZQj1NMsD6VsTXL'

# Tweepy
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

# APIインスタンスを作成
api = tweepy.API(auth, wait_on_rate_limit=True)


# for friend in tweepy.Cursor(api.friends).items():
#     print(friend.screen_name)


def limit_handled(cursor):
    while True:
        try:
            yield cursor.next()
        except tweepy.RateLimitError:
            time.sleep(1 * 5 )


for friend in limit_handled(tweepy.Cursor(api.friends).items()):
    print(friend)
