from fastapi.testclient import TestClient
from api.api_models.user import ProfileResponse
from api.api_models import user
from app import app


def test_get_user_by_id(client, test_user):
    login_res = client.post("/api/v1/users/login", data={"username": test_user["email"], "password": test_user["password"]})
    user_id = test_user["id"]
    profile_res = client.get(f"/api/v1/users/profile/{user_id}")

    assert profile_res.status_code == 200
    assert profile_res.json()["email"] == test_user["email"]

def test_update_profile(client,test_user):
    res=client.post(
      "/api/v1/users/login",
      data={
        "username": test_user.get("email"),
        "password": test_user.get("password")
      }
    )
    res_login = user.Token(**res.json())

    res = client.put(
        "/api/v1/users/profile",
        headers={"authorization": f"Bearer {res_login.token}"},
        json={
          "github_profile":"https://github.com/Slightly-Techie/",
          "twitter_profile":"https://twitter.com/slightlytechie",
          "linkedin_profile":"https://linkedin.com/slightlytechie"
      })
    
    get_res = client.get(
        "/api/v1/users/me",
        headers={"authorization": f"Bearer {res_login.token}"}
    )

    assert get_res.status_code == 200
    assert get_res.json()["github_profile"] == "https://github.com/Slightly-Techie/"

def test_get_current_user(client, test_user):
    login_res = client.post("/api/v1/users/login", data={"username": test_user["email"], "password": test_user["password"]})
    token = login_res.json()["token"]
    profile_res = client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token}"})
    
    assert profile_res.status_code == 200
    assert profile_res.json()["email"] == test_user["email"] 

def test_current_active_user(client, test_user):
    login_res = client.post("/api/v1/users/login", data={"username": test_user["email"], "password": test_user["password"]})
    token = login_res.json()["token"]
    profile_res = client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token}"})
    
    assert profile_res.status_code == 200
    assert profile_res.json()["email"] == test_user["email"]
    assert profile_res.json()["is_active"] == test_user["is_active"]

def test_current_inactive_user(client, inactive_user):
    login_res = client.post("/api/v1/users/login", data={"username": inactive_user["email"], "password": inactive_user["password"]})
    token = login_res.json()["token"]
    profile_res = client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token}"})
    
    assert profile_res.status_code == 200
    assert profile_res.json()["email"] == inactive_user["email"]
    assert profile_res.json()["is_active"] == inactive_user["is_active"]