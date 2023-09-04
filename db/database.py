from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from core.config import settings
from fastapi import Depends

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


def create_roles():   
    from db.models.roles import Role
    from utils.utils import RoleChoices

    db = SessionLocal()

    create_roles = [
    Role(name=RoleChoices.ADMIN),
    Role(name=RoleChoices.USER),
    Role(name=RoleChoices.GUEST)
    ]
    for role in create_roles:
        check_role = db.query(Role).filter(Role.name == role.name).first()
        if not check_role:
            db.add(role)

    db.commit()
    db.close()
