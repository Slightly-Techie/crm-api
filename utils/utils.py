import bcrypt
import os


def get_password_hash(password: str) -> str:
    # bcrypt requires bytes
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'), 
            hashed_password.encode('utf-8')
        )
    except Exception:
        return False


def is_image_file(file_name):
    image_formats = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.svg', '.ico'}
    _, file_extension = os.path.splitext(file_name)

    return file_extension.lower() in image_formats


class RoleChoices():
    ADMIN = 'admin'
    USER = 'user'
    GUEST = 'guest'


def get_key_by_value(value):
    experience_level_map = {
        "JUNIOR": [0, 1, 2],
        "MID_LEVEL": [3, 4],
        "SENIOR": [5, 6, 7, 8, 9, 10, 11, 12]
    }
    for key, values in experience_level_map.items():
        if value in values:
            return key
    return None
