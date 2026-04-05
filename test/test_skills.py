from fastapi.testclient import TestClient
from app import app

client = TestClient(app)


def test_populate_skills(client, test_user):
    login_res = client.post("/api/v1/users/login", data={"username": test_user["email"], "password": test_user["password"]})
    token = login_res.json()["token"]
    res = client.post("/api/v1/skills/data", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["message"] == "Skills table populated successfully!"


def test_get_all_skills(client, test_user, populate_skills):
    login_res = client.post("/api/v1/users/login", data={"username": test_user["email"], "password": test_user["password"]})
    token = login_res.json()["token"]
    res = client.get("/api/v1/skills/all", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert len(res.json()) == len(populate_skills)


# this is the same as test_add_skill
def test_get_user_skills(client, test_user, populate_skills):
    login_res = client.post("/api/v1/users/login", data={"username": test_user["email"], "password": test_user["password"]})
    token = login_res.json()["token"]
    res = client.post("/api/v1/skills/", json=[50,60], headers={'Authorization': f'Bearer {token}'})

    assert res.status_code == 201
    
    res = client.get("api/v1/skills/", headers={'Authorization': f'Bearer {token}'})
    
    assert res.status_code == 200
    assert len(res.json()) == 2


def test_unauthorized_get_user_skills(client, test_user, populate_skills):
    login_res = client.post("/api/v1/users/login", data={"username": test_user["email"], "password": test_user["password"]})
    token = login_res.json()["token"]
    res = client.post("/api/v1/skills/", json=[50,60], headers={'Authorization': f'Bearer {token}'})

    assert res.status_code == 201
    
    res = client.get("api/v1/skills/")

    assert res.status_code == 401

def test_add_skill_already_added(client, test_user, populate_skills):
    login_res = client.post("/api/v1/users/login", data={"username": test_user["email"], "password": test_user["password"]})
    token = login_res.json()["token"]
    res = client.post("/api/v1/skills/", json=[50,60], headers={'Authorization': f'Bearer {token}'})

    assert res.status_code == 201
    
    res = client.post("/api/v1/skills/", json=[60], headers={'Authorization': f'Bearer {token}'})

    assert res.status_code == 400

def test_unauthorized_add_skill(client):
    res = client.post("/api/v1/skills/", json=[50,60])

    assert res.status_code == 401

def test_delete_skill(client, test_user, populate_skills):
    login_res = client.post("/api/v1/users/login", data={"username": test_user["email"], "password": test_user["password"]})
    token = login_res.json()["token"]
    res = client.post("/api/v1/skills/", json=[50,60], headers={'Authorization': f'Bearer {token}'})

    assert res.status_code == 201
    
    res = client.delete("/api/v1/skills/50", headers={'Authorization': f'Bearer {token}'})

    assert res.status_code == 204

    res = client.get("api/v1/skills/", headers={'Authorization': f'Bearer {token}'})
    
    assert res.status_code == 200
    assert len(res.json()) == 1

def test_unauthorized_delete_skill(client, test_user, populate_skills):
    login_res = client.post("/api/v1/users/login", data={"username": test_user["email"], "password": test_user["password"]})
    token = login_res.json()["token"]
    res = client.post("/api/v1/skills/", json=[50,60], headers={'Authorization': f'Bearer {token}'})

    assert res.status_code == 201

    res = client.delete("/api/v1/skills/50")

    assert res.status_code == 401


def test_admin_can_create_skill_in_pool(client, test_user):
    login_res = client.post("/api/v1/users/login", data={"username": test_user["email"], "password": test_user["password"]})
    token = login_res.json()["token"]

    res = client.post(
        "/api/v1/skills/pool",
        json={"name": "React Native", "image_url": "https://example.com/s.png"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert res.status_code == 201
    assert res.json()["name"] == "React Native"


def test_non_admin_cannot_create_skill_in_pool(client, test_user1):
    login_res = client.post("/api/v1/users/login", data={"username": test_user1["email"], "password": test_user1["password"]})
    token = login_res.json()["token"]

    res = client.post(
        "/api/v1/skills/pool",
        json={"name": "AnotherNewSkill"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert res.status_code == 403


def test_admin_can_delete_skill_from_pool(client, test_user):
    login_res = client.post("/api/v1/users/login", data={"username": test_user["email"], "password": test_user["password"]})
    token = login_res.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    create_res = client.post(
        "/api/v1/skills/pool",
        json={"name": "DeleteMeSkill"},
        headers=headers,
    )
    assert create_res.status_code == 201

    skill_id = create_res.json()["id"]
    delete_res = client.delete(f"/api/v1/skills/pool/{skill_id}", headers=headers)
    assert delete_res.status_code == 204
