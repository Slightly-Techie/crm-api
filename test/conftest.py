from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.database import Base, get_db
from core.config import settings
from app import app
import pytest
from fastapi.testclient import TestClient
from db.models.users import Feed, Role
from utils.utils import RoleChoices

TEST_SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"

engine = create_engine(TEST_SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)


@pytest.fixture(autouse=True)
def create_roles(session):

    db = session

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


@pytest.fixture
def test_user(client):
    user = {
        "first_name": "Slightly",
        "last_name": "Techie",
        "email": "slightlytechie@gmail.com",
        "password": "food",
        "password_confirmation": "food",
        "role_id": 1,
        "years_of_experience": 5,
        "bio": "I am almost a techie",
        "phone_number": "233567895423",
        "profile_pic_url": "string",
        "is_active": True
    }
    res = client.post("/api/v1/users/register/", json=user)

    assert res.status_code == 201
    new_user = res.json()
    new_user["password"] = user.get("password")
    return new_user


@pytest.fixture
def inactive_user(client):
    user = {
        "first_name": "Jon",
        "last_name": "Doe",
        "email": "jondoe@gmail.com",
        "password": "jondoe",
        "password_confirmation": "jondoe",
        "years_of_experience": 1,
        "bio": "bio not needed",
        "phone_number": "233557932846",
        "profile_pic_url": "string",
        "is_active": False
    }
    res = client.post("/api/v1/users/register/", json=user)

    assert res.status_code == 201
    new_user = res.json()
    new_user["password"] = user.get("password")
    return new_user


@pytest.fixture
def test_user1(client):
    user = {
        "first_name": "Jane",
        "last_name": "Doe",
        "email": "janedoe@gmail.com",
        "password": "janedoe",
        "password_confirmation": "janedoe",
        "role_id": 2,
        "years_of_experience": 1,
        "bio": "bio not needed",
        "phone_number": "233557932846",
        "profile_pic_url": "string",
        "is_active": True
    }
    res = client.post("/api/v1/users/register/", json=user)

    assert res.status_code == 201
    new_user = res.json()
    new_user["password"] = user.get("password")
    return new_user


@pytest.fixture
def test_feeds(test_user, test_user1, session):
    db = session
    feed_data = [
        {"content": "content1", "user_id": test_user["id"]},
        {"content": "content2", "feed_pic_url": "feed_pic", "user_id": test_user["id"]},
        {"content": "content3", "user_id": test_user1["id"]},
        {"content": "content4", "user_id": test_user1["id"]},
    ]

    feeds = [Feed(**feed) for feed in feed_data]
    db.add_all(feeds)
    db.commit()
    feeds = db.query(Feed).all()

    return feeds