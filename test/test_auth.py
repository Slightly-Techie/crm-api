from datetime import datetime, timedelta

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from jose import jwt

from api.api_models.user import ForgotPasswordRequest, ResetPasswordRequest
from api.routes.auth import forgot_password, reset_password
from app import app
from core.config import settings
from db.models.users import User
from utils.oauth2 import create_reset_token, verify_reset_token

client = TestClient(app)

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

def test_user_signup_valid():
    res = client.post("/api/v1/users/register", json=user_signup_payload)
    res_body = res.json()

    assert res_body["email"] == user_signup_payload["email"]
    assert res.status_code == 201
    
def test_user_signup_invalid():
    res = client.post("/api/v1/users/register", json=user_signup_payload_incomplete)
    assert res.status_code == 422

def test_user_signup_invalid_confirm_password():
    payload = user_signup_payload.copy()
    payload["password_confirmation"] = "Test1235"
    res = client.post("/api/v1/users/register", json=payload)
    res_body = res.json()

    assert res.status_code == 400
    assert res_body["detail"] == settings.ERRORS.get("PASSWORD_MATCH_DETAIL")
    
def test_user_login_valid(test_user):
    res = client.post("/api/v1/users/login", data={
        "username": test_user.get("email"),
        "password": test_user.get("password")
    })
    res_body = res.json()

    assert res.status_code == 200
    assert res_body["token"] is not None
    
def test_user_login_invalid(test_user):
    res = client.post("/api/v1/users/login", data={
        "username": test_user.get("email"),
        "password": "Test1235"
    })
    res_body = res.json()

    assert res.status_code == 400
    assert res_body["detail"] == settings.ERRORS.get("INVALID_CREDENTIALS")

def test_user_gets_token_and_refresh_token(test_user):
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


def test_create_reset_token_valid_email(test_user, mocker):
    email = test_user.get("email")
    expected_token = 'valid_token'
    mocker.patch('jose.jwt.encode', return_value=expected_token)
    assert create_reset_token(email) == expected_token

def test_verify_reset_token_invalid_email_format():
    invalid_email = 'invalid_email'
    token = create_reset_token(invalid_email)
    with pytest.raises(HTTPException) as exc:
        verify_reset_token(token)
    assert exc.value.status_code == 400
    assert exc.value.detail == 'Invalid token'

def test_verify_reset_token_expired_token():
    email = 'test@example.com'
    delta = timedelta(minutes=-15)
    now = datetime.utcnow()
    payload = {
        'sub': email,
        'iat': now,
        'exp': now + delta
    }
    expired_token = jwt.encode(payload, settings.SECRET, algorithm=settings.ALGORITHM)
    with pytest.raises(HTTPException) as exc:
        verify_reset_token(expired_token)
    assert exc.value.status_code == 400

def test_forgot_password_email_sent_to_correct_address(test_user, mocker):
    expected_email = test_user.get("email")
    expected_token = "reset_token"

    mock_send_reset_password_email = mocker.patch('api.routes.auth.send_reset_password_email')
    mock_reset_token = mocker.patch('api.routes.auth.create_reset_token', return_value=expected_token)

    db = mocker.Mock()
    db.query.return_value.filter.return_value.first.return_value = User(email=expected_email)

    forgot_password(ForgotPasswordRequest(email=expected_email), db=db)
    mock_send_reset_password_email.assert_called_once_with(expected_email, mock_reset_token.return_value)

def test_forgot_password_user_not_found(test_user, mocker):
    db = mocker.Mock()
    db.query.return_value.filter.return_value.first.return_value = None
    with pytest.raises(HTTPException) as e:
        forgot_password(ForgotPasswordRequest(email=test_user.get("email")), db=db)
    assert e.value.status_code == 404
    assert e.value.detail == 'User not found'

def test_reset_password_invalid_token():
    with pytest.raises(HTTPException) as e:
        reset_password(ResetPasswordRequest(token='invalid_token', new_password='new_password'))
    assert e.value.status_code == 400
    assert e.value.detail == 'Invalid token'

