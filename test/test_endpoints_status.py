def test_create_endpoint_status(client, user_cred):
    # response = client.post("api/v1/endpoints/", json="signup", headers={"Authorization": f"{user_cred.token_type} {user_cred.token}"})
    # assert response.status_code == 200

    response = client.post("api/v1/endpoints/", json={"endpoint": "login"}, headers={"Authorization": f"{user_cred.token_type} {user_cred.token}"})
    assert response.status_code == 200


def test_unauthorized_create_endpoint_status(client):
    response = client.post("api/v1/endpoints/", json={"endpoint": "signup"})
    assert response.status_code == 401


# def test_toggle_endpoint_status(client, endpoints_status, user_cred):
#     response = client.put("api/v1/endpoints/", json="login", headers={"Authorization": f"{user_cred.token_type} {user_cred.token}"})
    
#     assert response.status_code == 200

def test_unauthorized_toggle_endpoint_status(client):
    response = client.post("api/v1/endpoints/", json={"endpoint": "signup"})
    assert response.status_code == 401

def test_endpoint_not_found(client, user_cred):
    response = client.put("api/v1/endpoints/", json={"endpoint": "get_users"}, headers={"Authorization": f"{user_cred.token_type} {user_cred.token}"})
    assert response.status_code == 404
