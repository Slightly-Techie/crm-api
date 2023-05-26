def test_create_tag(client, test_user):
    tag_name = "python"
    tag = {"name": tag_name}
    login_res = client.post("/api/v1/users/login", data={"username": test_user["email"], "password": test_user["password"]})
    token = login_res.json()["token"]
    res = client.post("/api/v1/users/tags", json=tag, headers={'Authorization': f'Bearer {token}'})

    assert res.status_code == 201
    data = res.json()
    assert data['id'] is not None
    assert data['name'] == tag["name"]

def test_create_tag_unauthenticated(client):
    tag_name = "python"
    tag = {"name": tag_name}
    res = client.post("/api/v1/users/tags", json=tag)

    assert res.status_code == 401

def test_get_tags(client, test_user):
    login_res = client.post("/api/v1/users/login", data={"username": test_user["email"], "password": test_user["password"]})
    token = login_res.json()["token"]
    res = client.get("/api/v1/users/tags", headers={'Authorization': f'Bearer {token}'})
    assert res.status_code == 200
    assert len(res.json().items()) > 0

def test_get_tags_unauthorized(client):
    res = client.get("/api/v1/users/tags")

    assert res.status_code == 401

def test_delete_tag(client, test_user):
    tag_name = "python"
    tag = {"name": tag_name}

    login_res = client.post("/api/v1/users/login", data={"username": test_user["email"], "password": test_user["password"]})
    token = login_res.json()["token"]
    
    res = client.post("/api/v1/users/tags", json=tag, headers={'Authorization': f'Bearer {token}'})
    data = res.json()
    res = client.delete(f"/api/v1/users/tags/{data['id']}", headers={'Authorization': f'Bearer {token}'})
    
    assert res.status_code == 204
    response = client.get("/api/v1/users/tags", headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
    assert tag not in response.json().items()

def test_delete_tag_unauthorized(client, test_user):
    tag_name = "python"
    tag = {"name": tag_name}

    login_res = client.post("/api/v1/users/login", data={"username": test_user["email"], "password": test_user["password"]})
    token = login_res.json()["token"]
    
    res = client.post("/api/v1/users/tags", json=tag, headers={'Authorization': f'Bearer {token}'})
    assert res.status_code == 201

    data = res.json()
    res = client.delete(f"/api/v1/users/tags/{data['id']}")

    assert res.status_code == 401
      