import pytest
from api.api_models.announcements import AnnouncementResponse

def test_get_all_announcements(client, test_announcements):
    response = client.get("/api/v1/announcements/?limit=50&page=1")
    assert response.status_code == 200
    announcements = response.json()
    assert len(announcements["items"]) == len(test_announcements)

    for i, announcement in enumerate(announcements["items"]):
        assert announcement["title"] == test_announcements[i].title
        assert announcement["content"] == test_announcements[i].content

def test_get_all_announcements_pagination(client, test_announcements):
    response = client.get("/api/v1/announcements?limit=2&page=1&size=50")
    assert response.status_code == 200
    announcements = response.json()
    assert len(announcements["items"]) == 2
    
    assert announcements["items"][0]["title"] == test_announcements[0].title
    assert announcements["items"][1]["content"] == test_announcements[1].content

def test_get_one_announcement(client, test_announcements):
    res = client.get(f"/api/v1/announcements/{test_announcements[0].id}")
    announcement = AnnouncementResponse(**res.json())
    assert announcement.id == test_announcements[0].id
    assert announcement.title == test_announcements[0].title
    assert announcement.content == test_announcements[0].content
    assert res.status_code == 200

def test_get_one_announcement_does_not_exist(client):
    res = client.get(f"api/v1/announcements/100")
    assert res.status_code == 404

@pytest.mark.parametrize(
    "title, content, image_url",
    [
        ("title1", "content1", "pic1"),
        ("title2", "content2", "pic2"),
        ("title3", "content3", None),
    ],
)
def test_create_announcement(client, test_user, title, content, image_url):
    payload = {
        "title": title, 
        "content": content, 
        "image_url": image_url,
    }

    login_res = client.post("/api/v1/users/login", data={"username": test_user["email"], "password": test_user["password"]})
    token = login_res.json()["token"]

    res = client.post("/api/v1/announcements/", json=payload, headers={'Authorization': f'Bearer {token}'})

    announcement = AnnouncementResponse(**res.json())

    assert res.status_code == 201
    assert announcement.title == title
    assert announcement.content == content
    assert announcement.image_url == image_url

def test_unauthorized_create_announcement(client):
    payload = {
        "title": "title1", 
        "content": "content1", 
        "image_url": "pic1",
    }

    res = client.post("/api/v1/announcements/", json=payload)

    assert res.status_code == 401

def test_unauthorized_delete_announcement(client, test_announcements):
    res = client.delete(f"/api/v1/announcements/{test_announcements[0].id}")

    assert res.status_code == 401

def test_delete_announcement(client, test_user, test_announcements):
    login_res = client.post("/api/v1/users/login", data={"username": test_user["email"], "password": test_user["password"]})
    token = login_res.json()["token"]
    res = client.delete(f"/api/v1/announcements/{test_announcements[0].id}", headers={'Authorization': f'Bearer {token}'})

    assert res.status_code == 204

def test_delete_announcement_does_not_exist(client, test_user):
    login_res = client.post("/api/v1/users/login", data={"username": test_user["email"], "password": test_user["password"]})
    token = login_res.json()["token"]
    res = client.delete(f"/api/v1/announcements/1000", headers={'Authorization': f'Bearer {token}'})

    assert res.status_code == 404

def test_update_announcements(client, test_user, test_announcements):
    login_res = client.post("/api/v1/users/login", data={"username": test_user["email"], "password": test_user["password"]})
    token = login_res.json()["token"]
    data = {"title": "update title", "content": "update content"}

    res = client.put(f"/api/v1/announcements/1", json=data, headers={'Authorization': f'Bearer {token}'})

    updated_announcement = AnnouncementResponse(**res.json())

    assert res.status_code == 200
    assert updated_announcement.id == 1
    assert updated_announcement.title == data["title"]
    assert updated_announcement.content == data["content"]

def test_unauthorized_update_announcements(client):
    data = {"title": "update title", "content": "update content"}
    res = client.put(f"/api/v1/announcements/1", json=data)

    assert res.status_code == 401

def test_update_announcements_does_not_exist(client, test_user):
    login_res = client.post("/api/v1/users/login", data={"username": test_user["email"], "password": test_user["password"]})
    token = login_res.json()["token"]
    data = {"title": "update title", "content": "update content"}

    res = client.put(f"/api/v1/announcements/100", json=data, headers={'Authorization': f'Bearer {token}'})

    assert res.status_code == 404
    
    