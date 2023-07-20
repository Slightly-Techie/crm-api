import pytest
from api.api_models.projects import CreateProject, ProjectResponse, UpdateProject


def test_create_project(client, test_user, test_user1):
    data = {"name": "Project 1", "description": "Description for Project 1", "manager_id": test_user1["id"],}

    login_res = client.post("/api/v1/users/login", data={"username": test_user["email"], "password": test_user["password"]})
    token = login_res.json()["token"]
    res = client.post("/api/v1/projects/", json=data, headers={'Authorization': f'Bearer {token}'})

    project = ProjectResponse(**res.json())

    assert res.status_code == 201
    assert project.name == data["name"]
    assert project.description == data["description"]
    
def test_unauthorized_user_create_project(client, test_user1):
    data = {"name": "Project 1", "description": "Description for Project 1", "manager_id": test_user1["id"],}

    login_res = client.post("/api/v1/users/login", data={"username": test_user1["email"], "password": test_user1["password"]})
    token = login_res.json()["token"]
    res = client.post("/api/v1/projects/", json=data, headers={'Authorization': f'Bearer {token}'})

    assert res.status_code == 403

def test_manager_not_exist(client, test_user, test_user1):
    data = {"name": "Project 1", "description": "Description for Project 1", "manager_id": 999,}

    login_res = client.post("/api/v1/users/login", data={"username": test_user["email"], "password": test_user["password"]})
    token = login_res.json()["token"]
    res = client.post("/api/v1/projects/", json=data, headers={'Authorization': f'Bearer {token}'})

    assert res.status_code == 404

def test_update_project(client, test_user, test_projects):
    login_res = client.post("/api/v1/users/login", data={"username": test_user["email"], "password": test_user["password"]})
    token = login_res.json()["token"]
    data = {"name": "update name", "description": "update description"}
    res = client.put(f"/api/v1/projects/{test_projects[0].id}", json=data, headers={"Authorization": f"Bearer {token}"})

    assert res.status_code == 201
    assert res.json()["name"] == data["name"]
    assert res.json()["description"] == data["description"]

def test_unauthorized_update_project(client, test_user1, test_projects):
    login_res = client.post("/api/v1/users/login", data={"username": test_user1["email"], "password": test_user1["password"]})
    token = login_res.json()["token"]
    data = {"name": "update name", "description": "update description"}
    res = client.put(f"/api/v1/projects/{test_projects[0].id}", json=data, headers={'Authorization': f'Bearer {token}'})

    assert res.status_code == 403

def test_update_project_does_not_exist(client, test_user, test_projects):
    login_res = client.post("/api/v1/users/login", data={"username": test_user["email"], "password": test_user["password"]})
    token = login_res.json()["token"]
    data = {"name": "update name", "description": "update description"}
    res = client.put(f"/api/v1/projects/1000", json=data, headers={"Authorization": f"Bearer {token}"})

    assert res.status_code == 404

def test_delete_project(client, test_user, test_projects):
    login_res = client.post("/api/v1/users/login", data={"username": test_user["email"], "password": test_user["password"]})
    token = login_res.json()["token"]
    res = client.delete(f"/api/v1/projects/{test_projects[0].id}", headers={"Authorization": f"Bearer {token}"})

    assert res.status_code == 204

def test_delete_project_does_not_exist(client, test_user, test_projects):
    login_res = client.post("/api/v1/users/login", data={"username": test_user["email"], "password": test_user["password"]})
    token = login_res.json()["token"]
    res = client.delete(f"/api/v1/projects/1000", headers={"Authorization": f"Bearer {token}"})

    assert res.status_code == 404

def test_unauthorized_delete_project(client, test_user1, test_projects):
    login_res = client.post("/api/v1/users/login", data={"username": test_user1["email"], "password": test_user1["password"]})
    token = login_res.json()["token"]
    res = client.delete(f"/api/v1/projects/{test_projects[0].id}", headers={'Authorization': f'Bearer {token}'})

    assert res.status_code == 403

def test_get_project(client, test_user, test_projects):
    login_res = client.post("/api/v1/users/login", data={"username": test_user["email"], "password": test_user["password"]})
    token = login_res.json()["token"]
    res = client.get(f"/api/v1/projects/{test_projects[0].id}", headers={"Authorization": f"Bearer {token}"})

    assert res.status_code == 200
    assert res.json()["name"] == test_projects[0].name
    assert res.json()["description"] == test_projects[0].description

def test_project_does_not_exist(client, test_user, test_projects):
    login_res = client.post("/api/v1/users/login", data={"username": test_user["email"], "password": test_user["password"]})
    token = login_res.json()["token"]
    res = client.get(f"/api/v1/projects/1000", headers={"Authorization": f"Bearer {token}"})

    assert res.status_code == 404

def test_get_all_projects(client, test_user, test_projects):
    login_res = client.post("/api/v1/users/login", data={"username": test_user["email"], "password": test_user["password"]})
    token = login_res.json()["token"]
    res = client.get("/api/v1/projects/", headers={"Authorization": f"Bearer {token}"})

    assert res.status_code == 200
    assert len(res.json()) == len(test_projects)
    assert res.json()[0]["name"] == test_projects[0].name
    assert res.json()[0]["description"] == test_projects[0].description

def test_add_user_to_project(client, test_user, test_user1, test_projects):
    login_res = client.post("/api/v1/users/login", data={"username": test_user1["email"], "password": test_user1["password"]})
    token = login_res.json()["token"]
    res = client.post(f"/api/v1/projects/{test_projects[0].id}/add/{test_user['id']}", headers={"Authorization": f"Bearer {token}"})

    assert res.status_code == 201
    assert res.json()["message"] == "User added to project"

def test_unauthorized_add_user_to_project(client, test_user, test_user1, test_projects):
    login_res = client.post("/api/v1/users/login", data={"username": test_user["email"], "password": test_user["password"]})
    token = login_res.json()["token"]
    res = client.post(f"/api/v1/projects/{test_projects[0].id}/add/{test_user1['id']}", headers={"Authorization": f"Bearer {token}"})

    assert res.status_code == 403

def test_add_user_to_project_does_not_exist(client, test_user, test_user1, test_projects):
    login_res = client.post("/api/v1/users/login", data={"username": test_user1["email"], "password": test_user1["password"]})
    token = login_res.json()["token"]
    res = client.post(f"/api/v1/projects/1000/add/{test_user['id']}", headers={"Authorization": f"Bearer {token}"})

    assert res.status_code == 403

def test_user_does_not_exist(client, test_user, test_user1, test_projects):
    login_res = client.post("/api/v1/users/login", data={"username": test_user1["email"], "password": test_user1["password"]})
    token = login_res.json()["token"]
    res = client.post(f"/api/v1/projects/{test_projects[0].id}/add/1000", headers={"Authorization": f"Bearer {token}"})

    assert res.status_code == 404

def test_remove_user_from_project(client, test_user1, test_user, test_projects):
    login_res = client.post("/api/v1/users/login", data={"username": test_user1["email"], "password": test_user1["password"]})
    token = login_res.json()["token"]
    res = client.post(f"/api/v1/projects/{test_projects[0].id}/add/{test_user['id']}", headers={"Authorization": f"Bearer {token}"})
    res = client.delete(f"/api/v1/projects/{test_projects[0].id}/remove/{test_user['id']}", headers={"Authorization": f"Bearer {token}"})

    assert res.status_code == 202
    assert res.json()["message"] == "User removed from project"


    