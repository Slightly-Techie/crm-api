
def test_admin_pagination(client):
    res=client.post(
      "/api/v1/admin/users/"
    )
    assert res.json().status_code == 202
    assert res.json()

