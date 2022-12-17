import pytest
from fastapi.testclient import TestClient
from api.api_models.user_response import UserResponse
from app import app

testclient = TestClient(app)

# def test_get_profile():
#     res = testclient.get("/api/v1/users/profile/?id=1")
    
#     assert res.status_code == 200

def test_get_profile(client):
    response = client.get("/api/v1/users/profile/?id=1")

    assert response.status_code == 200