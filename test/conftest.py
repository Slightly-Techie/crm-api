from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi import HTTPException
from db.database import Base, get_db
from core.config import settings
from app import app
import pytest
from fastapi.testclient import TestClient

from db.models.email_template import EmailTemplate
from db.models.endpoints import Endpoints
from db.models.roles import Role
from db.models.feeds import Feed
from db.models.stacks import Stack
from db.models.users import User
from db.models.announcements import Announcement
from api.api_models.user import (
    ForgotPasswordRequest,
    # UserSignUp
)
from utils.enums import EmailTemplateName
from utils.tools import tools as skills_data
from db.models.skills import Skill
from db.models.projects import Project
from utils.utils import RoleChoices
from api.routes.auth import (
    forgot_password,
    # reset_password
)
from api.api_models import user

pg_user = settings.POSTGRES_USER
pg_pass = settings.POSTGRES_PASSWORD
pg_host = settings.POSTGRES_SERVER
pg_port = settings.POSTGRES_PORT
pg_test_db = settings.POSTGRES_DB_TEST

TEST_SQLALCHEMY_DATABASE_URL = f"postgresql://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_test_db}"

engine = create_engine(TEST_SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine)


Base.metadata.drop_all(bind=engine)
# Base.metadata.create_all(bind=engine)


@pytest.fixture()
def session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


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


@pytest.fixture(autouse=True)
def create_signup_endpoint(session):
    db = session
    signup_endpoint_object = {
        "endpoint": "signup",
        "status": True
    }
    print(db.bind.url.database)
    signup_obj = db.query(Endpoints).filter(Endpoints.endpoint == signup_endpoint_object["endpoint"])
    if signup_obj.first():
        print("Endpoint found in db", signup_obj.first().status)
        if not signup_obj.first().status:
            print("Updating the status for signup")
            signup_obj.update({"status": True})
            db.commit()
            db.refresh(signup_obj)
            return True
    else:
        signup_object = Endpoints(
            endpoint=signup_endpoint_object["endpoint"],
            status=signup_endpoint_object["status"]
            )
        db.add(signup_object)
        db.commit()


@pytest.fixture
def test_user(client):
    user = {
        "username": "slightlytechie1",
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
        "username": "jondoe3",
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
        "username": "janedoe3",
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
def test_users(client, session):
    db = session
    users = [
        {
            "username": "slightlytechie",
            "first_name": "Slightly",
            "last_name": "Techie",
            "email": "slighttechie@gmail.com",
            "password": "food",
            "role_id": 1,
            "years_of_experience": 5,
            "bio": "I am almost a techie",
            "phone_number": "233567895423",
            "profile_pic_url": "string",
            "is_active": True
        },
        {
            "username": "jondoe3",
            "first_name": "Jon",
            "last_name": "Doe",
            "email": "jondoe@gmail.com",
            "password": "jondoe",
            "years_of_experience": 1,
            "bio": "bio not needed",
            "phone_number": "233557932846",
            "profile_pic_url": "string",
            "is_active": False
        },
        {
            "username": "janedoe3",
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "janedoe@gmail.com",
            "password": "janedoe",
            "role_id": 2,
            "years_of_experience": 1,
            "bio": "bio not needed",
            "phone_number": "233557932846",
            "profile_pic_url": "string",
            "is_active": True
        }
    ]

    db_users = []
    for user_data in users:
        user = User(**user_data)
        db_users.append(user)

    db.add_all(db_users)
    db.commit()
    users = db.query(User)

    return users


@pytest.fixture
def test_email_templates(test_user, test_user1, session):
    db = session
    template_Data = [
        {
            "template_name": EmailTemplateName.ACCEPTED,
            "subject": "Welcome to Slightly Techie!",
            "html_content": "<p>Hello World {} 1</p>"
        },
        {"template_name": EmailTemplateName.REJECTED,
            "subject": "Update on Application",
            "html_content": "<p>Hello World {} 2</p>"}]
    templates = [EmailTemplate(**template) for template in template_Data]
    db.add_all(templates)
    db.commit()
    email_templates = db.query(EmailTemplate).all()

    return email_templates


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


@pytest.fixture
def user_cred(client, test_user):
    res = client.post(
      "/api/v1/users/login",
      data={"username": test_user.get("email"), "password": test_user.get("password")}
    )
    user_credentials = user.Token(**res.json())

    return user_credentials


@pytest.fixture
def test_announcements(test_user, test_user1, session):
    db = session
    announcement_data = [
        {"title": "title1", "content": "content1", "user_id": test_user["id"]},
        {"title": "title2", "content": "content2", "user_id": test_user["id"]},
        {"title": "title3", "content": "content3", "user_id": test_user1["id"]},
        {"title": "title4", "content": "content4", "image_url": "image1", "user_id": test_user1["id"]},
    ]

    announcements = [Announcement(**announcement) for announcement in announcement_data]
    db.add_all(announcements)
    db.commit()
    announcements = db.query(Announcement).all()

    return announcements


@pytest.fixture
def mock_create_reset_token(mocker):
    return mocker.patch('api.routes.auth.create_reset_token', return_value="test_reset_token")


@pytest.fixture
def mock_send_email(mocker):
    return mocker.patch('utils.mail_service.send_email', return_value={"message": "Email has been sent"})


@pytest.mark.asyncio
async def test_forgot_password_user_not_found(mock_create_reset_token, mock_send_email, session):
    email = "nonexistent@example.com"
    db = session
    with pytest.raises(HTTPException) as e:
        await forgot_password(ForgotPasswordRequest(email=email), db=db)

    assert e.value.status_code == 404
    assert e.value.detail == 'User not found'

    mock_create_reset_token.assert_not_called()
    mock_send_email.assert_not_called()


@pytest.fixture
def test_projects(test_user, test_user1, session):
    db = session
    project_data = [
        {"name": "project1", "description": "description1", "project_type": "COMMUNITY",
         "project_priority": "LOW PRIORITY", "manager_id": test_user["id"]},
        {"name": "project2", "description": "description2", "project_type": "PAID",
         "project_priority": "MEDIUM PRIORITY", "manager_id": test_user["id"]},
        {"name": "project3", "description": "description3", "project_type": "COMMUNITY",
         "project_priority": "HIGH PRIORITY", "manager_id": test_user1["id"]},
        {"name": "project4", "description": "description4", "project_type": "PAID", "project_priority": "LOW PRIORITY",
         "manager_id": test_user1["id"]},
    ]

    projects = [Project(**project) for project in project_data]
    db.add_all(projects)
    db.commit()
    projects = db.query(Project).all()

    return projects


@pytest.fixture
def populate_skills(session):
    db = session
    skills = [Skill(name=skill) for skill in skills_data]
    db.add_all(skills)
    db.commit()
    skills = db.query(Skill).all()

    return skills


@pytest.fixture
def test_stacks(session):
    db = session
    stacks = [
        Stack(name='Backend'),
        Stack(name='Frontend'),
        Stack(name='DevOps'),
    ]
    db.add_all(stacks)
    db.commit()
    stacks = db.query(Stack).all()

    return stacks


@pytest.fixture
def endpoints_status(session):
    db = session
    endpoints_data = [Endpoints(endpoint="login"), Endpoints(endpoint="signup")]
    db.add_all(endpoints_data)
    db.commit()
    endpoints = db.query(Endpoints).all()

    return endpoints
