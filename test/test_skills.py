from api.routes.skills import populate_skills

def test_populate_skills(client):
    res = client.post("/api/v1/skills/data")
    assert res.status_code == 200
    assert res.json()["message"] == "Skills table populated successfully!"

def test_get_all_skills(client, populate_skills):
    res = client.get("/api/v1/skills/all")
    assert res.status_code == 200
    assert len(res.json()["items"]) == 50

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
    
def test_search_skills(client):
    res = client.post("/api/v1/skills/data")
    assert res.status_code == 200

    search_res = client.get("/api/v1/skills/search?name=pyton")
    search_result = search_res.json()
    assert search_res.status_code == 200
    assert all("skill_name" in item and "python" in item["skill_name"].lower() for item in search_result)
