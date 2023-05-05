def test_create_skill(client, test_user):
    skill_name = "backend development"
    skill = {"name": skill_name}
    login_res = client.post("/api/v1/users/login", data={"username": test_user["email"], "password": test_user["password"]})
    token = login_res.json()["token"]
    res = client.post("/api/v1/users/skills", json=skill, headers={'Authorization': f'Bearer {token}'})

    assert res.status_code == 201
    data = res.json()
    print(data)
    assert data['id'] is not None
    assert data['name'] == skill["name"]

def test_create_skill_unauthenticated(client):
    skill_name = "backend development"
    skill = {"name": skill_name}
    res = client.post("/api/v1/users/skills", json=skill)

    assert res.status_code == 401

def test_get_skills(client, test_user):
    login_res = client.post("/api/v1/users/login", data={"username": test_user["email"], "password": test_user["password"]})
    token = login_res.json()["token"]
    res = client.get("/api/v1/users/skills", headers={'Authorization': f'Bearer {token}'})
    assert res.status_code == 200
    assert len(res.json().items()) > 0

def test_get_skills_unauthorized(client):
    res = client.get("/api/v1/users/skills")

    assert res.status_code == 401

def test_delete_skill(client, test_user):
    skill_name = "backend development"
    skill = {"name": skill_name}

    login_res = client.post("/api/v1/users/login", data={"username": test_user["email"], "password": test_user["password"]})
    token = login_res.json()["token"]
    
    res = client.post("/api/v1/users/skills", json=skill, headers={'Authorization': f'Bearer {token}'})
    data = res.json()
    res = client.delete(f"/api/v1/users/skills/{data['id']}", headers={'Authorization': f'Bearer {token}'})
    
    assert res.status_code == 204
    response = client.get("/api/v1/users/skills", headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
    assert skill not in response.json().items()

def test_delete_skill_unauthorized(client, test_user):
    skill_name = "backend development"
    skill = {"name": skill_name}

    login_res = client.post("/api/v1/users/login", data={"username": test_user["email"], "password": test_user["password"]})
    token = login_res.json()["token"]
    
    res = client.post("/api/v1/users/skills", json=skill, headers={'Authorization': f'Bearer {token}'})
    assert res.status_code == 201

    data = res.json()
    res = client.delete(f"/api/v1/users/skills/{data['id']}")

    assert res.status_code == 401
      