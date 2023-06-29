from fastapi.testclient import TestClient
from api.api_models.user import ProfileResponse
from api.api_models import user
from app import app
from core.config import settings
from jose import jwt

user_signup_payload = {
    "first_name": "Slightly",
    "last_name": "Techie",
    "email": "test@slightlytechie.com",
    "password": "Test1234",
    "password_confirmation": "Test1234",
    "years_of_experience": 13,
    "bio": "I was born before the internet",
    "phone_number": "0501405002",
    "is_active": True
}

user_signup_payload_incomplete = {
    "first_name": "Slightly",
    "last_name": "Techie",
    "email": "test@slightlytechie.com",
    "password": "Test1234",
    "password_confirmation": "Test1234",
    "years_of_experience": 13,
    "is_active": True
}

def test_user_signup_valid(client):
    res = client.post("/api/v1/users/register", json=user_signup_payload)
    res_body = res.json()

    assert res_body["email"] == user_signup_payload["email"]
    assert res.status_code == 201
    
def test_user_signup_invalid(client):
    res = client.post("/api/v1/users/register", json=user_signup_payload_incomplete)
    assert res.status_code == 422

def test_user_signup_invalid_confirmpassword(client):
    payload = user_signup_payload.copy()
    payload["password_confirmation"] = "Test1235"
    res = client.post("/api/v1/users/register", json=payload)
    res_body = res.json()

    assert res.status_code == 400
    assert res_body["detail"] == settings.ERRORS.get("PASSWORD_MATCH_DETAIL")
    
def test_user_login_valid(client, test_user):
    res = client.post("/api/v1/users/login", data={
        "username": test_user.get("email"),
        "password": test_user.get("password")
    })
    res_body = res.json()

    assert res.status_code == 200
    assert res_body["token"] is not None
    
def test_user_login_invalid(client, test_user):
    res = client.post("/api/v1/users/login", data={
        "username": test_user.get("email"),
        "password": "Test1235"
    })
    res_body = res.json()

    assert res.status_code == 400
    assert res_body["detail"] == settings.ERRORS.get("INVALID_CREDENTIALS")

def test_user_gets_token_and_refreshtoken(client, test_user):
    login_response = client.post(
        "/api/v1/users/login",
        data={"username": test_user["email"], "password": test_user["password"]},
    )
    refresh_token = login_response.json()["refresh_token"]
    response = client.post(
        "/api/v1/users/refresh",
        json={"refresh_token": f"{refresh_token}"},
    )

    assert response.status_code == 200

    refresh_token_response = response.json()

    assert "token" in refresh_token_response
    assert "refresh_token" in refresh_token_response