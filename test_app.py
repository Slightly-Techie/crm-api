from fastapi.testclient import TestClient
from app import app
from db.database import engine, Base


Base.metadata.create_all(bind=engine)

client = TestClient(app)


def test_index():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"msg": "home"}
