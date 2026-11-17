from urllib.parse import urlsplit, parse_qs

from utils.mail_service import build_reset_password_url

EXPECTED_URL = "https://app.x.com/users/reset?token=abc123"


def test_base_without_slash_and_path_without_slash_get_one_slash():
    url = build_reset_password_url("https://app.x.com", "users/reset", "abc123")
    assert url == EXPECTED_URL


def test_base_with_slash_and_path_with_slash_get_no_double_slash():
    url = build_reset_password_url("https://app.x.com/", "/users/reset", "abc123")
    assert url == EXPECTED_URL


def test_base_without_slash_and_path_with_slash():
    url = build_reset_password_url("https://app.x.com", "/users/reset", "abc123")
    assert url == EXPECTED_URL


def test_base_with_slash_and_path_without_slash():
    url = build_reset_password_url("https://app.x.com/", "users/reset", "abc123")
    assert url == EXPECTED_URL


def test_path_on_base_url_is_kept():
    url = build_reset_password_url("https://x.com/crm", "users/reset", "abc123")
    assert url == "https://x.com/crm/users/reset?token=abc123"


def test_token_is_url_encoded():
    token = "a b+c/d=e&f"
    url = build_reset_password_url("https://app.x.com", "users/reset", token)

    query = urlsplit(url).query
    assert " " not in query
    assert "&" not in query
    assert parse_qs(query) == {"token": [token]}
