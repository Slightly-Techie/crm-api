from datetime import datetime, timedelta
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from jose import jwt
from unittest.mock import AsyncMock, patch

from api.api_models.user import ForgotPasswordRequest, ResetPasswordRequest
from api.routes.auth import forgot_password, reset_password
from app import app
from core.config import settings
from utils.oauth2 import create_reset_token, verify_reset_token


client = TestClient(app)

user_signup_payload = {
    "username": "slightlytechie1",
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
    "username": "slightlytechie1",
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


def test_reset_password_invalid_token():
    with pytest.raises(HTTPException) as e:
        reset_password(ResetPasswordRequest(token='invalid_token', new_password='new_password'))
    assert e.value.status_code == 400
    assert e.value.detail == 'Invalid token'



# Forgot Password Tests


@pytest.mark.asyncio
async def test_forgot_password_user_not_found(session):
    """Should raise 404 when the email doesn't match any user in the DB."""
    with pytest.raises(HTTPException) as exc:
        await forgot_password(
            ForgotPasswordRequest(email="ghost@nowhere.com"),
            db=session
        )
    assert exc.value.status_code == 404
    assert exc.value.detail == "User not found"


@pytest.mark.asyncio
async def test_forgot_password_success(test_user, session):
    """
    Happy path: user exists → reset token created → email dispatched.
    The SMTP call is mocked so no real email is sent.

    Flow traced here:
      POST /forgot-password
        → AuthService.forgot_password()
          → UserRepo.get_by_email()        ✓ user found
          → create_reset_token(email)      ✓ JWT built (mocked)
          → EmailTemplateRepo.get_by_name  ✓ returns None (empty DB table)
          → send_password_reset_email()
              → reads utils/email_templates/password-reset.html
              → injects {username} and {reset_url} into the template
              → send_email() → _send_email_sync() [MOCKED]
    """
    email = test_user["email"]

    # Mock SMTP so the test never opens a real connection
    with patch(
        "utils.mail_service._send_email_sync",
        return_value=None          # sync mock — to_thread wraps it
    ) as mock_smtp:
        response = await forgot_password(
            ForgotPasswordRequest(email=email),
            db=session
        )

    # _send_email_sync should have been called exactly once
    mock_smtp.assert_called_once()

    # The subject and recipient in the call args
    call_args = mock_smtp.call_args
    subject, recipient, html_body = call_args.args

    assert recipient == email
    assert "Slightly Techie" in subject          # matches email_subject fallback

    # Verify the HTML template was loaded and the username was injected
    username = test_user["username"]
    assert username in html_body                 # {0} → username substituted
    assert "reset" in html_body.lower()          # sanity: reset link present


@pytest.mark.asyncio
async def test_forgot_password_uses_db_template_when_present(test_user, session):
    """
    When a 'PASSWORD RESET' template exists in the DB, it should be used
    instead of the HTML file.
    """
    from db.models.email_template import EmailTemplate

    db_template = EmailTemplate(
        template_name="PASSWORD RESET",
        subject="Custom Reset Subject",
        html_content="<p>Hi {0}, click here: {1}</p>"
    )
    session.add(db_template)
    session.commit()

    email = test_user["email"]

    with patch("utils.mail_service._send_email_sync", return_value=None) as mock_smtp:
        await forgot_password(
            ForgotPasswordRequest(email=email),
            db=session
        )

    call_args = mock_smtp.call_args
    subject, recipient, html_body = call_args.args

    assert subject == "Custom Reset Subject"     # DB template subject used
    assert test_user["username"] in html_body    # {0} substituted with username
    assert "http" in html_body                   # {1} substituted with reset URL


def test_forgot_password_via_http_user_not_found(client):
    """End-to-end HTTP test: unknown email → 404."""
    res = client.post(
        "/api/v1/users/forgot-password",
        json={"email": "nobody@example.com"}
    )
    assert res.status_code == 404
    assert res.json()["detail"] == "User not found"


def test_forgot_password_via_http_success(client, test_user):
    """
    End-to-end HTTP test: registered user email → 200.
    SMTP is mocked at the module level so no real email is sent.
    """
    with patch("utils.mail_service._send_email_sync", return_value=None):
        res = client.post(
            "/api/v1/users/forgot-password",
            json={"email": test_user["email"]}
        )

    assert res.status_code == 200
    assert res.json()["message"] == "Email sent successfully"

