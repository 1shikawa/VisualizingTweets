from pydantic import BaseModel
from typing import List

class StockIn(BaseModel):
    tweet_id: str
    screen_name: str
    user_id: str
    tweet_text: str
    tweet_url: str
    favorite_count: int
    retweet_count: int
    expanded_url: str



class StockOut(StockIn):
    id: int
    tweet_id: str
    screen_name: str
    user_id: str
    tweet_text: str
    tweet_url: str
    favorite_count: int
    retweet_count: int
    expanded_url: str


class StockUpdate(StockIn):
    pass
