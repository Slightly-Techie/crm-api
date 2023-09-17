import pytest
from api.api_models.user import Feeds, FeedUpdate


def test_get_all_feeds(client, test_feeds):
    response = client.get("/api/v1/feed/")
    assert response.status_code == 200
    feeds = response.json()
    assert len(feeds["feeds"]) == len(test_feeds)

    for i, feed in enumerate(feeds["feeds"]):
        assert feed["content"] == test_feeds[i].content
        assert feed["user"]["id"] == test_feeds[i].user.id


def test_get_all_feeds_pagination(client, test_feeds, session):
    response = client.get("/api/v1/feed/?limit=2&skip=0&page=1&size=50")
    feeds = response.json()

    assert len(feeds["feeds"]) == 2
    assert response.status_code == 200
    assert feeds["feeds"][1]["content"] == test_feeds[1].content
    assert feeds["feeds"][1]["user"]["id"] == test_feeds[1].user.id


def test_get_one_feed(client, test_feeds):
    res = client.get(f"/api/v1/feed/{test_feeds[0].id}")
    feed = Feeds(**res.json())
    assert feed.id == test_feeds[0].id
    assert feed.content == test_feeds[0].content
    assert feed.user.id == test_feeds[0].user.id
    assert res.status_code == 200


def test_get_one_feed_does_not_exist(client, test_feeds):
    res = client.get(f"api/v1/feed/10000")
    assert res.status_code == 404


@pytest.mark.parametrize(
    "content, feed_pic_url",
    [
        ("content1", "pic1"),
        ("content2", "pic2"),
        ("content3", None),
    ],
)
def test_create_feed(client, test_user, test_feeds, content, feed_pic_url):
    payload = {"content": content, "feed_pic_url": feed_pic_url,}
    login_res = client.post("/api/v1/users/login", data={"username": test_user["email"], "password": test_user["password"]})
    token = login_res.json()["token"]
    res = client.post("/api/v1/feed/", json=payload, headers={'Authorization': f'Bearer {token}'})

    feed = Feeds(**res.json())

    assert res.status_code == 201
    assert feed.content == content
    assert feed.feed_pic_url == feed_pic_url
    assert feed.user.id == test_user["id"]


def test_unauthorized_user_create_feed(client, test_feeds):
    res = client.post("/api/v1/feed/", json={"content": "content4", "feed_pic_url": "feed_pic_url"})
    assert res.status_code == 401


def test_unauthorized_user_delete_feed(client, test_feeds, test_user):
    res = client.delete(f"/api/v1/feed/{test_feeds[0].id}")

    assert res.status_code == 401

def test_user_delete_feed(client, test_feeds, test_user):
    login_res = client.post("/api/v1/users/login", data={"username": test_user["email"], "password": test_user["password"]})
    token = login_res.json()["token"]
    res = client.delete(f"/api/v1/feed/{test_feeds[0].id}", headers={'Authorization': f'Bearer {token}'})

    assert res.status_code == 204


def test_authorized_user_delete_feed_does_not_exist(client, test_feeds, test_user):
    login_res = client.post("/api/v1/users/login", data={"username": test_user["email"], "password": test_user["password"]})
    token = login_res.json()["token"]
    res = client.delete("/api/v1/feed/1000", headers={'Authorization': f'Bearer {token}'})

    assert res.status_code == 404


def test_delete_other_user_feed(client, test_feeds, test_user):
    login_res = client.post("/api/v1/users/login", data={"username": test_user["email"], "password": test_user["password"]})
    token = login_res.json()["token"]
    res = client.delete(f"/api/v1/feed/{test_feeds[3].id}", headers={'Authorization': f'Bearer {token}'})

    assert res.status_code == 403


def test_update_feed(client, test_feeds, test_user):
    login_res = client.post("/api/v1/users/login", data={"username": test_user["email"], "password": test_user["password"]})
    token = login_res.json()["token"]
    data = {"content": "update content", "feed_pic_url": "updated_pic"}

    res = client.put(f"/api/v1/feed/{test_feeds[0].id}", json=data, headers={'Authorization': f'Bearer {token}'})
    updated_feed = FeedUpdate(**res.json())
    assert res.status_code == 201
    assert updated_feed.content == data["content"]


def test_update_other_user_feed(client, test_user1, test_feeds, test_user):
    login_res = client.post("/api/v1/users/login", data={"username": test_user["email"], "password": test_user["password"]})
    token = login_res.json()["token"]
    data = {"content": "update content", "feed_pic_url": "updated_pic"}

    res = client.put(f"/api/v1/feed/{test_feeds[3].id}", json=data, headers={'Authorization': f'Bearer {token}'})
    assert res.status_code == 403

def test_unauthorized_user_update_feed(client, test_feeds, test_user):
    res = client.put(f"/api/v1/feed/{test_feeds[0].id}")

    assert res.status_code == 401

def test_authorized_user_update_feed_does_not_exist(client, test_feeds, test_user):
    login_res = client.post("/api/v1/users/login", data={"username": test_user["email"], "password": test_user["password"]})
    token = login_res.json()["token"]
    data = {"content": "update content", "feed_pic_url": "updated_pic"}

    res = client.put("/api/v1/feed/10000", json=data, headers={'Authorization': f'Bearer {token}'})
    assert res.status_code == 404