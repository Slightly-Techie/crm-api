import os
from dotenv import load_dotenv

from pathlib import Path
env_path = Path('.') / '.env'
load_dotenv()


class Settings:
    PROJECT_NAME: str = "Job Board"
    PROJECT_VERSION: str = "1.0.0"

    POSTGRES_USER: "str | None" = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_SERVER: "str | None" = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_PORT: "str | int" = os.getenv(
        "POSTGRES_PORT", 5432)  # default postgres port is 5432
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "postgres")
    POSTGRES_DB_TEST: str = os.getenv("POSTGRES_DB_TEST", "postgres")
    DATABASE_URL = os.getenv(
        "DATABASE_URL", f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}")
    SECRET: str = os.getenv("SECRET", "ABnfjEINSKl3ECmsnoINEnwmkWAS")
    REFRESH_SECRET: str = os.getenv(
        "REFRESH_SECRET", "NIk10kHWwa2Fbl6Pt46E+OSiC1h6")
    PRODUCTION_ENV: bool = os.getenv("PRODUCTION_ENV", False)
    REFRESH_TOKEN_EXPIRE_MINUTES: int = os.getenv(
        "REFRESH_TOKEN_EXPIRE_MINUTES", 60*24*30)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = os.getenv(
        "ACCESS_TOKEN_EXPIRE_MINUTES", 60*24*2)
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ERRORS: dict = {
        "INVALID_CREDENTIALS": "Invalid Credentials",
        "PASSWORD_MATCH_DETAIL": "Passwords do not match",
        "USER_EXISTS": "User with email already exists",
        "INVALID ID": "ID does not exist",
        "UNKNOWN ERROR": "Something went wrong",
        "USER ALREADY ACTIVE": "User is already active",
    }
    BASE_URL: str = os.getenv("BASE_URL")
    EMAIL_SERVER: str = os.getenv("EMAIL_SERVER", "smtp.gmail.com")
    EMAIL_PORT: int = os.getenv("EMAIL_PORT", 465)
    AWS_BUCKET_NAME: str = os.getenv("AWS_BUCKET_NAME", "aws_bucket_name")
    AWS_REGOIN: str = os.getenv("AWS_REGION", "us-east-1")
    AWS_ACCESS_KEY: str = os.getenv("AWS_ACCESS_KEY", "aws_access_key")
    AWS_SECRET_KEY: str = os.getenv("AWS_SECRET_KEY", "aws_secret_key")
    EMAIL_SENDER: str = os.getenv("EMAIL_SENDER", "slightly.techie@gmail.com")
    EMAIL_PASSWORD: str = os.getenv("EMAIL_PASSWORD")
    URL_PATH: str = os.getenv("URL_PATH")


settings = Settings()
