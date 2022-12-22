from fastapi.testclient import TestClient
from api.api_models.user import ProfileResponse
from app import app


def test_get_profile(client,test_user):
    res = client.get("/api/v1/users/profile/?id=1")

    assert test_user.get("email") == "slightlytechie@gmail.com"
    assert res.status_code == 200,res.text

def test_update_profile(client,test_user):
    res = client.put("/api/v1/users/profile/?id=1",json={"github_profile":"https://github.com/Slightly-Techie/","twitter_profile":"https://twitter.com/slightlytechie","linkedin_profile":"https://linkedin.com/slightlytechie"})
    

    assert test_user.get("github_profile") == "https://github.com/Slightly-Techie/"
    assert res.status_code == 200
    
   