import pytest

from utils.utils import get_password_hash, verify_password, is_image_file, normalize_profile_url


def test_verify_password():
    password_hash = get_password_hash("hello world")
    assert verify_password(
        "hello world", password_hash)

def test_valid_image_file():
    valid_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.svg', '.ico'}
    for extension in valid_extensions:
        file_name = f"image{extension}"
        assert is_image_file(file_name)

def test_invalid_image_file():
    invalid_extensions = {'.pdf', '.doc', '.xlsx', '.txt', '.zip', '.csv'}
    for extension in invalid_extensions:
        file_name = f"not_image{extension}"
        assert not is_image_file(file_name)


@pytest.mark.parametrize("value, expected", [
    ("github.com/ransfordgenesis", "https://github.com/ransfordgenesis"),
    ("https://x.com/a", "https://x.com/a"),
    ("http://example.com", "http://example.com"),
    ("  linkedin.com/in/kobi  ", "https://linkedin.com/in/kobi"),
    ("//example.com/me", "https://example.com/me"),
    ("localhost:3000/me", "https://localhost:3000/me"),
    ("", None),
    (None, None),
])
def test_normalize_profile_url(value, expected):
    assert normalize_profile_url(value) == expected


@pytest.mark.parametrize("value", [
    "javascript:alert(1)",
    "JavaScript:alert(1)",
    "java\tscript:alert(1)",
    "data:text/html,<script>alert(1)</script>",
    "mailto:someone@example.com",
    "https://",
])
def test_normalize_profile_url_rejects_unsafe_links(value):
    with pytest.raises(ValueError):
        normalize_profile_url(value)
