from utils.utils import get_password_hash, verify_password


def test_verify_password():
    password_hash = get_password_hash("hello world")
    assert verify_password(
        "hello world", password_hash)


