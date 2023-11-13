from api.api_models import user
from fastapi_pagination import add_pagination


def test_get_user_by_id(client, test_user):
    login_res = client.post(
        "/api/v1/users/login", data={"username": test_user["email"], "password": test_user["password"]})
    user_id = test_user["id"]
    profile_res = client.get(f"/api/v1/users/profile/{user_id}")

    assert profile_res.status_code == 200
    assert profile_res.json()["email"] == test_user["email"]


def test_update_profile(client, test_user):
    res = client.post(
        "/api/v1/users/login",
        data={
            "username": test_user.get("email"),
            "password": test_user.get("password")
        }
    )
    res_login = user.Token(**res.json())

    res = client.put(
        "/api/v1/users/profile",
        headers={"authorization": f"Bearer {res_login.token}"},
        json={
            "github_profile": "https://github.com/Slightly-Techie/",
            "twitter_profile": "https://twitter.com/slightlytechie",
            "linkedin_profile": "https://linkedin.com/slightlytechie"
        })

    get_res = client.get(
        "/api/v1/users/me",
        headers={"authorization": f"Bearer {res_login.token}"}
    )

    assert get_res.status_code == 200
    assert get_res.json()[
        "github_profile"] == "https://github.com/Slightly-Techie/"


def test_get_current_user(client, test_user):
    login_res = client.post(
        "/api/v1/users/login", data={"username": test_user["email"], "password": test_user["password"]})
    token = login_res.json()["token"]
    profile_res = client.get(
        "/api/v1/users/me", headers={"Authorization": f"Bearer {token}"})

    assert profile_res.status_code == 200
    assert profile_res.json()["email"] == test_user["email"]


def test_current_active_user(client, test_user):
    login_res = client.post(
        "/api/v1/users/login", data={"username": test_user["email"], "password": test_user["password"]})
    token = login_res.json()["token"]
    profile_res = client.get(
        "/api/v1/users/me", headers={"Authorization": f"Bearer {token}"})

    assert profile_res.status_code == 200
    assert profile_res.json()["email"] == test_user["email"]
    assert profile_res.json()["is_active"] == test_user["is_active"]


# Test update profile status
def test_update_profile_status(client, test_user, inactive_user):
    # Given a test_user who is an admin and an inactive_user
    login_data = {"username": test_user["email"],
                  "password": test_user["password"]}

    # When the test_user logs in and updates the inactive_user's profile status to active
    login_res = client.post("/api/v1/users/login", data=login_data)
    token = login_res.json()["token"]
    user_id = inactive_user["id"]
    headers = {"Authorization": f"Bearer {token}"}
    activate_res = client.put(
        f"/api/v1/users/profile/{user_id}/activate", headers=headers)

    # Then the inactive_user's profile status should be active
    assert activate_res.status_code == 200
    assert activate_res.json()["is_active"] is True


def test_activate_already_active_user(client, test_user):
    # Given a test_user who is an admin and an active_user
    login_res = client.post(
        "/api/v1/users/login", data={"username": test_user["email"], "password": test_user["password"]})
    token = login_res.json()["token"]
    user_id = test_user["id"]

    # When the test_user tries to activate the active_user's profile
    profile_res = client.put(
        f"/api/v1/users/profile/{user_id}/activate", headers={"Authorization": f"Bearer {token}"})

    # Then the active_user's profile status should not change
    assert profile_res.status_code == 400
    assert profile_res.json()["detail"] == "User is already active"


def test_activate_invalid_user_profile(client, test_user):
    # Given a test_user who is an admin and an invalid user ID
    login_res = client.post(
        "/api/v1/users/login", data={"username": test_user["email"], "password": test_user["password"]})
    token = login_res.json()["token"]
    user_id = 9999

    # When the test_user tries to activate the invalid user's profile
    response = client.put(
        f"/api/v1/users/profile/{user_id}/activate",
        headers={"Authorization": f"Bearer {token}"}
    )

    # Then the response should be unsuccessful with a 404 Not Found status code
    assert response.status_code == 404
    
def test_get_user_info(client, test_user):
    # Given a test_user
    email = test_user["email"]

    # When the test_user requests user information based on email
    response = client.get(
        f"/api/v1/users/user_info?email={email}"
    )

    # Then the response should be successful with a 200 OK status code
    assert response.status_code == 200
    assert "first_name" in response.json()["data"]
    assert "last_name" in response.json()["data"]
    assert "phone_number" in response.json()["data"]

def test_search_users(client, test_users):
    response = client.get("/api/v1/users/search?p=doe&page=1&size=2")

    assert response.status_code == 200
    assert len(response.json()["items"]) == 2

    response = client.get("/api/v1/users/search?p=doe&page=1&size=1")
    assert len(response.json()["items"]) == 1

def test_search_user_not_found(client, test_users):
    response = client.get("/api/v1/users/search?p=notfound&page=1&size=2")

    assert response.status_code == 404
    