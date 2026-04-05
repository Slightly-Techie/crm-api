def _auth_header(client, email: str, password: str) -> dict:
    res = client.post("/api/v1/users/login", data={"username": email, "password": password})
    assert res.status_code == 200, res.text
    token = res.json()["token"]
    return {"Authorization": f"Bearer {token}"}


def _meeting_payload(title: str = "Weekly Sync") -> dict:
    return {
        "title": title,
        "meeting_url": "https://meet.google.com/abc-defg-hij",
        "description": "Weekly team sync",
        "recurrence": "weekly",
    }


def test_admin_can_create_meeting(client, test_user):
    headers = _auth_header(client, test_user["email"], test_user["password"])
    res = client.post("/api/v1/weekly-meetings/", json=_meeting_payload(), headers=headers)
    assert res.status_code == 201
    assert res.json()["title"] == "Weekly Sync"


def test_non_admin_cannot_create_meeting(client, test_user1):
    headers = _auth_header(client, test_user1["email"], test_user1["password"])
    res = client.post("/api/v1/weekly-meetings/", json=_meeting_payload(), headers=headers)
    assert res.status_code == 403


def test_authenticated_user_can_get_meetings(client, test_user, test_user1, session):
    from db.models.users import User
    from utils.enums import UserStatus
    db_user1 = session.query(User).filter(User.id == test_user1["id"]).first()
    db_user1.status = UserStatus.ACCEPTED
    session.commit()

    admin_headers = _auth_header(client, test_user["email"], test_user["password"])
    user_headers = _auth_header(client, test_user1["email"], test_user1["password"])

    create_res = client.post(
        "/api/v1/weekly-meetings/",
        json=_meeting_payload("Engineering Standup"),
        headers=admin_headers,
    )
    assert create_res.status_code == 201

    list_res = client.get("/api/v1/weekly-meetings/", headers=user_headers)
    assert list_res.status_code == 200
    assert len(list_res.json()["items"]) >= 1


def test_get_active_meeting(client, test_user, test_user1, session):
    from db.models.users import User
    from utils.enums import UserStatus
    db_user1 = session.query(User).filter(User.id == test_user1["id"]).first()
    db_user1.status = UserStatus.ACCEPTED
    session.commit()

    admin_headers = _auth_header(client, test_user["email"], test_user["password"])
    user_headers = _auth_header(client, test_user1["email"], test_user1["password"])

    create_res = client.post(
        "/api/v1/weekly-meetings/",
        json=_meeting_payload("Active Meeting"),
        headers=admin_headers,
    )
    assert create_res.status_code == 201

    active_res = client.get("/api/v1/weekly-meetings/active", headers=user_headers)
    assert active_res.status_code == 200
    assert active_res.json()["title"] == "Active Meeting"


def test_admin_can_update_meeting(client, test_user):
    headers = _auth_header(client, test_user["email"], test_user["password"])

    create_res = client.post("/api/v1/weekly-meetings/", json=_meeting_payload(), headers=headers)
    assert create_res.status_code == 201
    meeting_id = create_res.json()["id"]

    update_res = client.put(
        f"/api/v1/weekly-meetings/{meeting_id}",
        json={"title": "Updated Sync", "is_active": False},
        headers=headers,
    )
    assert update_res.status_code == 200
    assert update_res.json()["title"] == "Updated Sync"
    assert update_res.json()["is_active"] is False


def test_non_admin_cannot_update_meeting(client, test_user, test_user1):
    admin_headers = _auth_header(client, test_user["email"], test_user["password"])
    user_headers = _auth_header(client, test_user1["email"], test_user1["password"])

    create_res = client.post("/api/v1/weekly-meetings/", json=_meeting_payload(), headers=admin_headers)
    meeting_id = create_res.json()["id"]

    update_res = client.put(
        f"/api/v1/weekly-meetings/{meeting_id}",
        json={"title": "Should Not Update"},
        headers=user_headers,
    )
    assert update_res.status_code == 403


def test_admin_can_delete_meeting(client, test_user):
    headers = _auth_header(client, test_user["email"], test_user["password"])

    create_res = client.post("/api/v1/weekly-meetings/", json=_meeting_payload(), headers=headers)
    meeting_id = create_res.json()["id"]

    delete_res = client.delete(f"/api/v1/weekly-meetings/{meeting_id}", headers=headers)
    assert delete_res.status_code == 204
