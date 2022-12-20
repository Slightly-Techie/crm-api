from fastapi.testclient import TestClient
from api.api_models.user import UserResponse
from app import app

testclient = TestClient(app)

def test_get_profile():
    res = testclient.get("/api/v1/users/profile/?id=1")
    
    assert res.status_code == 200

def test_update_profile():
    res = testclient.put("/api/v1/users/profile/?id=1",json={"github_profile":"https://github.com/Slightly-Techie/","twitter_profile":"https://twitter.com/slightlytechie","linkedin_profile":"https://linkedin.com/slightlytechie","portfolio_url":""})
   
    assert res.status_code == 200
   