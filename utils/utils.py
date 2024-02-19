from passlib.context import CryptContext
import os

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain_password, password):
    return pwd_context.verify(plain_password, password)


def is_image_file(file_name):
    image_formats = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.svg', '.ico'}
    _, file_extension = os.path.splitext(file_name)

    return file_extension.lower() in image_formats


class RoleChoices():
    ADMIN = 'admin'
    USER = 'user'
    GUEST = 'guest'
