import os
from dotenv import load_dotenv

from pathlib import Path
env_path = Path('.') / '.env'
load_dotenv()

class Settings:
    PROJECT_NAME:str = "Job Board"
    PROJECT_VERSION: str = "1.0.0"

    POSTGRES_USER : "str | None" = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_SERVER : "str | None" = os.getenv("POSTGRES_SERVER","localhost")
    POSTGRES_PORT : "str | int" = os.getenv("POSTGRES_PORT",5432) # default postgres port is 5432
    POSTGRES_DB : str = os.getenv("POSTGRES_DB","postgres")
    DATABASE_URL = os.getenv("DATABASE_URL",f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}")
    SECRET: str = os.getenv("SECRET", "ABnfjEINSKl3ECmsnoINEnwmkWAS")
    PRODUCTION_ENV : bool = os.getenv("PRODUCTION_ENV", False)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60*24*30)
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ERRORS: dict = {
        "INVALID_CREDENTIALS": "Invalid Credentials",
        "PASSWORD_MATCH_DETAIL": "Passwords do not match",
        "USER_EXISTS": "User with email already exists",
        "INVALID ID":"ID does not exist",
        "UNKNOWN ERROR":"Something went wrong"
    }
    
settings = Settings()
