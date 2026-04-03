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
    # Map years of experience to ExperienceLevel enum values
    from utils.enums import ExperienceLevel

    experience_level_map = {
        ExperienceLevel.JUNIOR.value: [0, 1, 2],
        ExperienceLevel.MID_LEVEL.value: [3, 4],
        ExperienceLevel.SENIOR.value: [5, 6, 7, 8, 9, 10, 11, 12]
    }
    for key, values in experience_level_map.items():
        if value in values:
            return key
    raise ValueError(
        f"Invalid years_of_experience value: {value}. "
        f"Must be between 0 and 12. Valid ranges: Junior (0-2), Mid-level (3-4), Senior (5-12)."
    )
