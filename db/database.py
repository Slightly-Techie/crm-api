from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from core.config import settings

SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"



def set_up_db(production_env):
    if production_env:
        engine = create_engine(settings.DATABASE_URL)
    else:
        engine = create_engine(
        SQLALCHEMY_DATABASE_URL)    
    SessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()
    return engine, SessionLocal, Base


engine, SessionLocal, Base = set_up_db(settings.PRODUCTION_ENV)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
