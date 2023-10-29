from utils.utils import get_password_hash, verify_password, is_image_file


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
