from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from core.config import settings

pg_user = settings.POSTGRES_USER
pg_pass = settings.POSTGRES_PASSWORD
pg_server = settings.POSTGRES_SERVER
pg_port = settings.POSTGRES_PORT
pg_db = settings.POSTGRES_DB
SQLALCHEMY_DATABASE_URL = f"postgresql://{pg_user}:{pg_pass}@{pg_server}:{pg_port}/{pg_db}"


def set_up_db(production_env):
    if production_env:
        engine = create_engine(settings.DATABASE_URL)
    else:
        engine = create_engine(SQLALCHEMY_DATABASE_URL)
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
