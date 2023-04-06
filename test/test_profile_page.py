from fastapi.testclient import TestClient
from api.api_models.user import ProfileResponse
from api.api_models import user
from app import app


def test_get_profile(client,test_user):
    res=client.post(
      "/api/v1/users/login" , data={"username": test_user.get("email"), "password": test_user.get("password")}
    )
    res_login = user.Token(**res.json())
    profile_res = client.get("/api/v1/users/profile/", headers={"authorization": f"Bearer {res_login.token}"})

    assert profile_res.json().get("email") == test_user.get("email")
    assert profile_res.status_code == 200

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
        "/api/v1/users/profile/",
        headers={"authorization": f"Bearer {res_login.token}"},
        json={
          "github_profile":"https://github.com/Slightly-Techie/",
          "twitter_profile":"https://twitter.com/slightlytechie",
          "linkedin_profile":"https://linkedin.com/slightlytechie"
      })
    

    assert test_user.get("github_profile") == "https://github.com/Slightly-Techie/"
    assert res.status_code == 200
    
   