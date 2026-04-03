import pytest

from utils.enums import UserStatus


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _auth_header(client, email: str, password: str) -> dict:
    """Log in and return an Authorization header dict."""
    res = client.post("/api/v1/users/login", data={"username": email, "password": password})
    assert res.status_code == 200, res.text
    token = res.json()["token"]
    return {"Authorization": f"Bearer {token}"}


def _make_admin_accepted(session, user_dict):
    """Set the user's status to ACCEPTED in the DB (needed for user_accepted guard)."""
    from db.models.users import User
    u = session.query(User).filter(User.id == user_dict["id"]).first()
    u.status = UserStatus.ACCEPTED
    session.commit()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def admin_headers(client, test_user):
    """Auth headers for test_user (role_id=1, admin)."""
    return _auth_header(client, test_user["email"], test_user["password"])


@pytest.fixture
def user_headers(client, test_user1):
    """Auth headers for test_user1 (role_id=2, regular user)."""
    return _auth_header(client, test_user1["email"], test_user1["password"])


@pytest.fixture
def accepted_user_headers(client, test_user1, session):
    """Auth headers for test_user1 with ACCEPTED status."""
    _make_admin_accepted(session, test_user1)
    return _auth_header(client, test_user1["email"], test_user1["password"])


@pytest.fixture
def accepted_admin_headers(client, test_user, session):
    """Auth headers for test_user (admin) with ACCEPTED status."""
    _make_admin_accepted(session, test_user)
    return _auth_header(client, test_user["email"], test_user["password"])


@pytest.fixture
def org_tree(client, test_user, test_user1, session, admin_headers):
    """Build a small org tree: test_user -> test_user1 (test_user is manager of test_user1)."""
    res = client.patch(
        f"/api/v1/users/{test_user1['id']}/manager",
        json={"manager_id": test_user["id"]},
        headers=admin_headers,
    )
    assert res.status_code == 200, res.text
    return {"root": test_user, "child": test_user1}


# ===========================================================================
# ADMIN ENDPOINTS
# ===========================================================================


class TestAdminGetFullOrgChart:
    """GET /api/v1/users/org-chart (admin only)"""

    def test_returns_roots(self, client, test_user, test_user1, admin_headers, session):
        # Make users ACCEPTED so they appear in org chart
        _make_admin_accepted(session, test_user)
        _make_admin_accepted(session, test_user1)

        res = client.get("/api/v1/users/org-chart", headers=admin_headers)
        assert res.status_code == 200
        data = res.json()
        # Both users have no manager → both are roots
        root_ids = {node["id"] for node in data}
        assert test_user["id"] in root_ids
        assert test_user1["id"] in root_ids

    def test_returns_tree_structure(self, client, org_tree, admin_headers, session):
        # Make users ACCEPTED so they appear in org chart
        _make_admin_accepted(session, org_tree["root"])
        _make_admin_accepted(session, org_tree["child"])

        res = client.get("/api/v1/users/org-chart", headers=admin_headers)
        assert res.status_code == 200
        data = res.json()
        # Only root should be test_user (test_user1 now has a manager)
        root_ids = {node["id"] for node in data}
        assert org_tree["root"]["id"] in root_ids
        assert org_tree["child"]["id"] not in root_ids
        # The child should appear in the root's subordinates
        root_node = next(n for n in data if n["id"] == org_tree["root"]["id"])
        sub_ids = {s["id"] for s in root_node["subordinates"]}
        assert org_tree["child"]["id"] in sub_ids

    def test_max_depth_param(self, client, org_tree, admin_headers):
        # max_depth=1 should include root but NOT recurse into child's children
        res = client.get("/api/v1/users/org-chart?max_depth=1", headers=admin_headers)
        assert res.status_code == 200

    def test_forbidden_for_non_admin(self, client, user_headers):
        res = client.get("/api/v1/users/org-chart", headers=user_headers)
        assert res.status_code == 403

    def test_unauthorized_without_token(self, client):
        res = client.get("/api/v1/users/org-chart")
        assert res.status_code == 401


class TestAdminGetSubordinates:
    """GET /api/v1/users/{user_id}/subordinates (admin only)"""

    def test_returns_direct_reports(self, client, org_tree, admin_headers):
        res = client.get(
            f"/api/v1/users/{org_tree['root']['id']}/subordinates",
            headers=admin_headers,
        )
        assert res.status_code == 200
        sub_ids = {s["id"] for s in res.json()}
        assert org_tree["child"]["id"] in sub_ids

    def test_empty_subordinates(self, client, org_tree, admin_headers):
        res = client.get(
            f"/api/v1/users/{org_tree['child']['id']}/subordinates",
            headers=admin_headers,
        )
        assert res.status_code == 200
        assert res.json() == []

    def test_user_not_found(self, client, admin_headers):
        res = client.get("/api/v1/users/99999/subordinates", headers=admin_headers)
        assert res.status_code == 404

    def test_forbidden_for_non_admin(self, client, test_user, user_headers):
        res = client.get(
            f"/api/v1/users/{test_user['id']}/subordinates",
            headers=user_headers,
        )
        assert res.status_code == 403


class TestAdminGetUserOrgChart:
    """GET /api/v1/users/{user_id}/org-chart (admin only)"""

    def test_returns_subtree(self, client, org_tree, admin_headers, session):
        # Make users ACCEPTED so they appear in org chart
        _make_admin_accepted(session, org_tree["root"])
        _make_admin_accepted(session, org_tree["child"])

        res = client.get(
            f"/api/v1/users/{org_tree['root']['id']}/org-chart",
            headers=admin_headers,
        )
        assert res.status_code == 200
        data = res.json()
        assert data["id"] == org_tree["root"]["id"]
        sub_ids = {s["id"] for s in data["subordinates"]}
        assert org_tree["child"]["id"] in sub_ids

    def test_leaf_node_subtree(self, client, org_tree, admin_headers, session):
        # Make users ACCEPTED so they appear in org chart
        _make_admin_accepted(session, org_tree["root"])
        _make_admin_accepted(session, org_tree["child"])

        res = client.get(
            f"/api/v1/users/{org_tree['child']['id']}/org-chart",
            headers=admin_headers,
        )
        assert res.status_code == 200
        data = res.json()
        assert data["id"] == org_tree["child"]["id"]
        assert data["subordinates"] == []

    def test_user_not_found(self, client, admin_headers):
        res = client.get("/api/v1/users/99999/org-chart", headers=admin_headers)
        assert res.status_code == 404

    def test_forbidden_for_non_admin(self, client, test_user, user_headers):
        res = client.get(
            f"/api/v1/users/{test_user['id']}/org-chart",
            headers=user_headers,
        )
        assert res.status_code == 403


class TestUpdateManager:
    """PATCH /api/v1/users/{user_id}/manager (admin only)"""

    def test_assign_manager(self, client, test_user, test_user1, admin_headers):
        res = client.patch(
            f"/api/v1/users/{test_user1['id']}/manager",
            json={"manager_id": test_user["id"]},
            headers=admin_headers,
        )
        assert res.status_code == 200
        assert res.json()["manager_id"] == test_user["id"]

    def test_remove_manager(self, client, org_tree, admin_headers):
        res = client.patch(
            f"/api/v1/users/{org_tree['child']['id']}/manager",
            json={"manager_id": None},
            headers=admin_headers,
        )
        assert res.status_code == 200
        assert res.json()["manager_id"] is None

    def test_self_manager_rejected(self, client, test_user, admin_headers):
        res = client.patch(
            f"/api/v1/users/{test_user['id']}/manager",
            json={"manager_id": test_user["id"]},
            headers=admin_headers,
        )
        assert res.status_code == 422
        assert "own manager" in res.json()["detail"].lower()

    def test_circular_reference_rejected(self, client, org_tree, admin_headers):
        # org_tree: root -> child.  Try to make root report to child.
        res = client.patch(
            f"/api/v1/users/{org_tree['root']['id']}/manager",
            json={"manager_id": org_tree["child"]["id"]},
            headers=admin_headers,
        )
        assert res.status_code == 422
        assert "circular" in res.json()["detail"].lower()

    def test_manager_not_found(self, client, test_user, admin_headers):
        res = client.patch(
            f"/api/v1/users/{test_user['id']}/manager",
            json={"manager_id": 99999},
            headers=admin_headers,
        )
        assert res.status_code == 404

    def test_user_not_found(self, client, admin_headers):
        res = client.patch(
            "/api/v1/users/99999/manager",
            json={"manager_id": 1},
            headers=admin_headers,
        )
        assert res.status_code == 404

    def test_forbidden_for_non_admin(self, client, test_user, user_headers):
        res = client.patch(
            f"/api/v1/users/{test_user['id']}/manager",
            json={"manager_id": None},
            headers=user_headers,
        )
        assert res.status_code == 403


# ===========================================================================
# SELF-SCOPED ENDPOINTS (accepted users)
# ===========================================================================


class TestGetMyManager:
    """GET /api/v1/users/me/manager"""

    def test_returns_manager(self, client, org_tree, session, accepted_user_headers):
        # test_user1 (accepted) has test_user as manager
        _make_admin_accepted(session, org_tree["child"])
        headers = accepted_user_headers
        res = client.get("/api/v1/users/me/manager", headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert data["id"] == org_tree["root"]["id"]

    def test_returns_null_when_no_manager(self, client, accepted_admin_headers):
        res = client.get("/api/v1/users/me/manager", headers=accepted_admin_headers)
        assert res.status_code == 200
        assert res.json() is None

    def test_forbidden_for_non_accepted_user(self, client, user_headers):
        res = client.get("/api/v1/users/me/manager", headers=user_headers)
        assert res.status_code == 403


class TestGetMySubordinates:
    """GET /api/v1/users/me/subordinates"""

    def test_returns_subordinates(self, client, org_tree, session, accepted_admin_headers):
        # test_user (admin, accepted) is manager of test_user1
        res = client.get("/api/v1/users/me/subordinates", headers=accepted_admin_headers)
        assert res.status_code == 200
        sub_ids = {s["id"] for s in res.json()}
        assert org_tree["child"]["id"] in sub_ids

    def test_returns_empty_when_no_subordinates(self, client, test_user1, session, accepted_user_headers):
        res = client.get("/api/v1/users/me/subordinates", headers=accepted_user_headers)
        assert res.status_code == 200
        assert res.json() == []

    def test_forbidden_for_non_accepted_user(self, client, user_headers):
        res = client.get("/api/v1/users/me/subordinates", headers=user_headers)
        assert res.status_code == 403


# ===========================================================================
# ACCEPTED-USER VIEW ENDPOINTS
# ===========================================================================


class TestAcceptedUserViewEndpoints:
    """/api/v1/users/view/{user_id}/... endpoints (accepted users)"""

    def test_view_user_manager(self, client, org_tree, accepted_user_headers, session):
        _make_admin_accepted(session, org_tree["child"])
        res = client.get(
            f"/api/v1/users/view/{org_tree['child']['id']}/manager",
            headers=accepted_user_headers,
        )
        assert res.status_code == 200
        assert res.json()["id"] == org_tree["root"]["id"]

    def test_view_user_subordinates(self, client, org_tree, accepted_user_headers, session):
        _make_admin_accepted(session, org_tree["child"])
        res = client.get(
            f"/api/v1/users/view/{org_tree['root']['id']}/subordinates",
            headers=accepted_user_headers,
        )
        assert res.status_code == 200
        sub_ids = {s["id"] for s in res.json()}
        assert org_tree["child"]["id"] in sub_ids

    def test_view_user_org_chart(self, client, org_tree, accepted_user_headers, session):
        # Make both users ACCEPTED so they appear in org chart
        _make_admin_accepted(session, org_tree["root"])
        _make_admin_accepted(session, org_tree["child"])

        res = client.get(
            f"/api/v1/users/view/{org_tree['root']['id']}/org-chart",
            headers=accepted_user_headers,
        )
        assert res.status_code == 200
        assert res.json()["id"] == org_tree["root"]["id"]

    def test_view_endpoints_forbidden_for_non_accepted(self, client, org_tree, user_headers):
        res = client.get(
            f"/api/v1/users/view/{org_tree['root']['id']}/manager",
            headers=user_headers,
        )
        assert res.status_code == 403


# ===========================================================================
# BULK ASSIGN SUBORDINATES
# ===========================================================================


class TestBulkAssignSubordinates:
    """POST /api/v1/users/assign-subordinates?manager_id={id}"""

    def test_assign_multiple_subordinates(self, client, test_user, test_user1, inactive_user, admin_headers):
        res = client.post(
            f"/api/v1/users/assign-subordinates?manager_id={test_user['id']}",
            json={"user_ids": [test_user1["id"], inactive_user["id"]]},
            headers=admin_headers,
        )
        assert res.status_code == 200
        data = res.json()
        assert len(data["updated"]) == 2
        updated_ids = {u["id"] for u in data["updated"]}
        assert test_user1["id"] in updated_ids
        assert inactive_user["id"] in updated_ids
        # Verify via subordinates endpoint
        subs = client.get(
            f"/api/v1/users/{test_user['id']}/subordinates",
            headers=admin_headers,
        )
        sub_ids = {s["id"] for s in subs.json()}
        assert test_user1["id"] in sub_ids
        assert inactive_user["id"] in sub_ids

    def test_assign_single_subordinate(self, client, test_user, test_user1, admin_headers):
        res = client.post(
            f"/api/v1/users/assign-subordinates?manager_id={test_user['id']}",
            json={"user_ids": [test_user1["id"]]},
            headers=admin_headers,
        )
        assert res.status_code == 200
        assert len(res.json()["updated"]) == 1

    def test_manager_not_found(self, client, test_user1, admin_headers):
        res = client.post(
            "/api/v1/users/assign-subordinates?manager_id=99999",
            json={"user_ids": [test_user1["id"]]},
            headers=admin_headers,
        )
        assert res.status_code == 404

    def test_some_user_ids_not_found(self, client, test_user, test_user1, admin_headers):
        res = client.post(
            f"/api/v1/users/assign-subordinates?manager_id={test_user['id']}",
            json={"user_ids": [test_user1["id"], 99999]},
            headers=admin_headers,
        )
        assert res.status_code == 200
        data = res.json()
        assert len(data["updated"]) == 1
        assert 99999 in data["not_found"]

    def test_manager_cannot_be_in_subordinate_list(self, client, test_user, admin_headers):
        res = client.post(
            f"/api/v1/users/assign-subordinates?manager_id={test_user['id']}",
            json={"user_ids": [test_user["id"]]},
            headers=admin_headers,
        )
        assert res.status_code == 422
        assert "own subordinate" in res.json()["detail"].lower()

    def test_circular_reference_rejected(self, client, org_tree, admin_headers):
        # org_tree: root -> child.  Try to make root a subordinate of child.
        res = client.post(
            f"/api/v1/users/assign-subordinates?manager_id={org_tree['child']['id']}",
            json={"user_ids": [org_tree["root"]["id"]]},
            headers=admin_headers,
        )
        assert res.status_code == 422
        assert "circular" in res.json()["detail"].lower()

    def test_empty_user_ids(self, client, test_user, admin_headers):
        res = client.post(
            f"/api/v1/users/assign-subordinates?manager_id={test_user['id']}",
            json={"user_ids": []},
            headers=admin_headers,
        )
        assert res.status_code == 422

    def test_forbidden_for_non_admin(self, client, test_user, user_headers):
        res = client.post(
            f"/api/v1/users/assign-subordinates?manager_id={test_user['id']}",
            json={"user_ids": [1]},
            headers=user_headers,
        )
        assert res.status_code == 403

    def test_unauthorized_without_token(self, client, test_user):
        res = client.post(
            f"/api/v1/users/assign-subordinates?manager_id={test_user['id']}",
            json={"user_ids": [1]},
        )
        assert res.status_code == 401


# ===========================================================================
# DELETE USER — SUBORDINATE REASSIGNMENT
# ===========================================================================


class TestDeleteUserReassignment:
    """DELETE /api/v1/users/{user_id}
    When a manager is deleted, their subordinates should be reassigned
    to the deleted user's manager (not set to NULL).
    """

    def test_subordinates_reassigned_to_grandparent(
        self, client, test_user, test_user1, inactive_user, admin_headers, session
    ):
        """A -> B -> C.  Delete B.  C should now report to A."""
        # Build chain: test_user -> test_user1 -> inactive_user
        client.patch(
            f"/api/v1/users/{test_user1['id']}/manager",
            json={"manager_id": test_user["id"]},
            headers=admin_headers,
        )
        client.patch(
            f"/api/v1/users/{inactive_user['id']}/manager",
            json={"manager_id": test_user1["id"]},
            headers=admin_headers,
        )

        # Delete the middle manager (test_user1)
        res = client.delete(
            f"/api/v1/users/{test_user1['id']}",
            headers=admin_headers,
        )
        assert res.status_code == 204

        # inactive_user should now report to test_user
        subs = client.get(
            f"/api/v1/users/{test_user['id']}/subordinates",
            headers=admin_headers,
        )
        sub_ids = {s["id"] for s in subs.json()}
        assert inactive_user["id"] in sub_ids

    def test_subordinates_become_roots_when_deleted_user_has_no_manager(
        self, client, test_user, test_user1, admin_headers, session
    ):
        """A -> B.  Delete A (root).  B should become a root (manager_id=NULL)."""
        client.patch(
            f"/api/v1/users/{test_user1['id']}/manager",
            json={"manager_id": test_user["id"]},
            headers=admin_headers,
        )

        res = client.delete(
            f"/api/v1/users/{test_user['id']}",
            headers=admin_headers,
        )
        assert res.status_code == 204

        # test_user1 should now be a root in the org chart
        # Need to log in as test_user1 (who must be admin to view org chart)
        # Instead, check directly via DB
        from db.models.users import User
        u = session.query(User).filter(User.id == test_user1["id"]).first()
        assert u is not None
        assert u.manager_id is None

    def test_delete_user_not_found(self, client, admin_headers):
        res = client.delete("/api/v1/users/99999", headers=admin_headers)
        assert res.status_code == 404

    def test_delete_forbidden_for_non_admin(self, client, test_user, user_headers):
        res = client.delete(
            f"/api/v1/users/{test_user['id']}",
            headers=user_headers,
        )
        assert res.status_code == 403
