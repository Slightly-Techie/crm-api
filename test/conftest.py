from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.database import Base, get_db
from core.config import settings
from app import app
import pytest
from fastapi.testclient import TestClient

TEST_SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"

engine = create_engine(TEST_SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


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


@pytest.fixture
def test_user(client):
    user = {
        "first_name": "Slightly",
        "last_name": "Techie",
        "email": "slightlytechie@gmail.com",
        "password": "food",
        "password_confirmation": "food",
        "years_of_experience": 5,
        "bio": "I am almost a techie",
        "phone_number": "233567895423",
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
        "is_active": False
    }
    res = client.post("/api/v1/users/register/", json=user)

    assert res.status_code == 201
    new_user = res.json()
    new_user["password"] = user.get("password")
    return new_user
