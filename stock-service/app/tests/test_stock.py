from starlette.testclient import TestClient
from app.main import app
from app.api.database import metadata, database, engine

client = TestClient(app)


def test_post_stock():
    response = client.post('api/v1/stock/', json={
            "tweet_id": "string",
            "screen_name": "string",
            "user_id": "string",
            "tweet_text": "string",
            "tweet_url": "string",
            "favorite_count": 0,
            "retweet_count": 0,
            "expanded_url": "string"
        }
    )

    assert response.status_code == 200


def test_get_stocks():
    response = client.get('api/v1/stock/')
    assert response.status_code == 200


def test_get_stock():
    response = client.get('api/v1/stock/1/')
    assert response.status_code == 200


def test_put_stock():
    response = client.put('api/v1/stock/1/')
    assert response.status_code == 200


def test_delete_stock():
    response = client.delete('api/v1/stock/1/')
    assert response.status_code == 200
