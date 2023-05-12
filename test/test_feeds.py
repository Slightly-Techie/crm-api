from api.api_models.user import Feeds


def test_get_all_feeds(client, test_feeds):
    response = client.get("/api/v1/feed/")
    assert response.status_code == 200
    feeds = response.json()
    assert len(feeds["feeds"]) == len(test_feeds)

    for i, feed in enumerate(feeds["feeds"]):
        assert feed["title"] == test_feeds[::-1][i].title
        assert feed["content"] == test_feeds[::-1][i].content
        assert feed["user"]["id"] == test_feeds[::-1][i].user.id


def test_get_all_feeds_pagination(client, test_feeds, session):
    response = client.get("/api/v1/feed/?limit=2&skip=0&page=1&size=50")
    assert response.status_code == 200
    feeds = response.json()
    assert len(feeds["feeds"]) == 2
    
    assert feeds["feeds"][0]["title"] == test_feeds[::-1][0].title
    assert feeds["feeds"][1]["content"] == test_feeds[::-1][1].content
    assert feeds["feeds"][1]["user"]["id"] == test_feeds[::-1][1].user.id


def test_get_one_feed(client, test_feeds):
    res = client.get(f"/api/v1/feed/{test_feeds[0].id}")
    feed = Feeds(**res.json())
    assert feed.id == test_feeds[0].id
    assert feed.title == test_feeds[0].title
    assert feed.content == test_feeds[0].content
    assert feed.user.id == test_feeds[0].user.id
    assert res.status_code == 200


def test_get_one_post_does_not_exist(client, test_feeds):
    res = client.get(f"api/v1/feed/10000")
    assert res.status_code == 404
