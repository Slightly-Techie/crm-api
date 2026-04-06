def _auth_header(client, email: str, password: str) -> dict:
    res = client.post("/api/v1/users/login", data={"username": email, "password": password})
    assert res.status_code == 200, res.text
    token = res.json()["token"]
    return {"Authorization": f"Bearer {token}"}


def _challenge_payload(title: str = "Two Sum") -> dict:
    return {
        "title": title,
        "description": "Find two numbers that add up to target",
        "challenge_type": "LEETCODE",
        "difficulty": "Easy",
        "challenge_url": "https://leetcode.com/problems/two-sum/",
    }


def test_admin_can_create_challenge(client, test_user):
    headers = _auth_header(client, test_user["email"], test_user["password"])
    res = client.post("/api/v1/coding-challenges/", json=_challenge_payload(), headers=headers)
    assert res.status_code == 201
    assert res.json()["title"] == "Two Sum"


def test_non_admin_cannot_create_challenge(client, test_user1):
    headers = _auth_header(client, test_user1["email"], test_user1["password"])
    res = client.post("/api/v1/coding-challenges/", json=_challenge_payload(), headers=headers)
    assert res.status_code == 403


def test_authenticated_user_can_get_challenges(client, test_user, test_user1, session):
    from db.models.users import User
    from utils.enums import UserStatus
    db_user1 = session.query(User).filter(User.id == test_user1["id"]).first()
    db_user1.status = UserStatus.ACCEPTED
    session.commit()

    admin_headers = _auth_header(client, test_user["email"], test_user["password"])
    user_headers = _auth_header(client, test_user1["email"], test_user1["password"])

    create_res = client.post(
        "/api/v1/coding-challenges/",
        json=_challenge_payload("Valid Parentheses"),
        headers=admin_headers,
    )
    assert create_res.status_code == 201

    list_res = client.get("/api/v1/coding-challenges/", headers=user_headers)
    assert list_res.status_code == 200
    assert len(list_res.json()["items"]) >= 1


def test_get_latest_challenge(client, test_user, test_user1, session):
    from db.models.users import User
    from utils.enums import UserStatus
    db_user1 = session.query(User).filter(User.id == test_user1["id"]).first()
    db_user1.status = UserStatus.ACCEPTED
    session.commit()

    admin_headers = _auth_header(client, test_user["email"], test_user["password"])
    user_headers = _auth_header(client, test_user1["email"], test_user1["password"])

    first = client.post(
        "/api/v1/coding-challenges/",
        json=_challenge_payload("First Challenge"),
        headers=admin_headers,
    )
    assert first.status_code == 201

    second = client.post(
        "/api/v1/coding-challenges/",
        json={**_challenge_payload("Second Challenge"), "difficulty": "Medium"},
        headers=admin_headers,
    )
    assert second.status_code == 201

    latest_res = client.get("/api/v1/coding-challenges/latest", headers=user_headers)
    assert latest_res.status_code == 200
    assert latest_res.json()["title"] == "Second Challenge"


def test_admin_can_update_challenge(client, test_user):
    headers = _auth_header(client, test_user["email"], test_user["password"])

    create_res = client.post("/api/v1/coding-challenges/", json=_challenge_payload(), headers=headers)
    challenge_id = create_res.json()["id"]

    update_res = client.put(
        f"/api/v1/coding-challenges/{challenge_id}",
        json={"title": "Updated Challenge", "difficulty": "Hard"},
        headers=headers,
    )
    assert update_res.status_code == 200
    assert update_res.json()["title"] == "Updated Challenge"
    assert update_res.json()["difficulty"] == "Hard"


def test_non_admin_cannot_update_challenge(client, test_user, test_user1):
    admin_headers = _auth_header(client, test_user["email"], test_user["password"])
    user_headers = _auth_header(client, test_user1["email"], test_user1["password"])

    create_res = client.post("/api/v1/coding-challenges/", json=_challenge_payload(), headers=admin_headers)
    challenge_id = create_res.json()["id"]

    update_res = client.put(
        f"/api/v1/coding-challenges/{challenge_id}",
        json={"title": "Should Not Update"},
        headers=user_headers,
    )
    assert update_res.status_code == 403


def test_admin_can_delete_challenge(client, test_user):
    headers = _auth_header(client, test_user["email"], test_user["password"])

    create_res = client.post("/api/v1/coding-challenges/", json=_challenge_payload(), headers=headers)
    challenge_id = create_res.json()["id"]

    delete_res = client.delete(f"/api/v1/coding-challenges/{challenge_id}", headers=headers)
    assert delete_res.status_code == 204
