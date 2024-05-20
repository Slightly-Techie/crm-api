def test_create_endpoint_status(client):
    response = client.post("api/v1/endpoints/", json="signup")
    assert response.status_code == 200

    response = client.post("api/v1/endpoints/", json="login")
    assert response.status_code == 200


def test_toggle_endpoint_status(client, endpoints_status):
    response = client.put("api/v1/endpoints/", json="login")
    
    assert response.status_code == 200


def test_endpoint_not_found(client):
    response = client.put("api/v1/endpoints/", json="get_users")
    assert response.status_code == 404
