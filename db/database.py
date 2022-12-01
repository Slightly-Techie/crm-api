from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from core.config import settings

TEST_SQLALCHEMY_DATABASE_URL = ""


def set_up_db(production_env=False):
    if production_env:
        engine = create_engine(settings.DATABASE_URL)
    else:
        engine = create_engine(
        TEST_SQLALCHEMY_DATABASE_URL)    
    SessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()
    return engine, SessionLocal, Base


engine, SessionLocal, Base = set_up_db(production_env=True)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
