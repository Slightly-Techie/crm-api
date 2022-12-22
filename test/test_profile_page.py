from fastapi.testclient import TestClient
from api.api_models.user import ProfileResponse
from app import app

testclient = TestClient(app)

def test_get_profile(client):
    res = client.get("/api/v1/users/profile/?id=1")

    res_json = ProfileResponse(**res.json())

    assert res_json.email == "slightlytechie@gmail.com"
    assert res.status_code == 200,res.text

def test_update_profile(client):
    res = client.put("/api/v1/users/profile/?id=1",json={"github_profile":"https://github.com/Slightly-Techie/","twitter_profile":"https://twitter.com/slightlytechie","linkedin_profile":"https://linkedin.com/slightlytechie"})
    
    res_json = ProfileResponse(**res.json())

    assert res_json.github_profile == "https://github.com/Slightly-Techie/"
    assert res.status_code == 200
    
   