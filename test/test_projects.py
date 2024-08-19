import pytest
from fastapi import status


project_url = "/api/v1/projects/"


def test_create_project(session, client, user_cred, test_projects):
    url = project_url

    data = {
        "name": "test_project",
        "description": "test_description",
        "project_type": "COMMUNITY",
        "project_priority": "HIGH PRIORITY",
        # "project_tools": [68, 25],
        "manager_id": 1
    }

    res = client.post(url, json=data, headers={"Authorization": f"{user_cred.token_type} {user_cred.token}"})
    res_data = res.json()

    assert res.status_code == status.HTTP_201_CREATED
    assert res_data['name'] == data['name']


def test_create_project_manager_not_found(session, client, user_cred, test_projects):
    url = project_url

    data = {
        "name": "test_project",
        "description": "test_description",
        "project_type": "COMMUNITY",
        "project_priority": "HIGH PRIORITY",
        # "project_tools": [68, 25],
        "manager_id": 100
    }

    res = client.post(url, json=data, headers={"Authorization": f"{user_cred.token_type} {user_cred.token}"})

    assert res.status_code == status.HTTP_404_NOT_FOUND


def test_create_project_not_authorized(client, test_projects):
    url = project_url

    data = {
        "name": "test_project",
        "description": "test_description",
        "project_type": "COMMUNITY",
        "project_priority": "HIGH PRIORITY",
        # "project_tools": [68, 25],
        "manager_id": 1
    }
    res = client.post(url, json=data)

    assert res.status_code == 401


def test_get_all_projects(client, test_projects):
    response = client.get(f"{project_url}?page=1&size=2")
    assert response.status_code == 200
    projects = response.json()
    assert len(projects["items"]) == 2

    assert projects["items"][0]["name"] == test_projects[0].name  


def test_get_project(session, client, test_projects):
    url = project_url + str(test_projects[0].id)

    res = client.get(url)
    res_data = res.json()

    assert res.status_code == status.HTTP_200_OK
    assert res_data['name'] == test_projects[0].name


def test_get_project_not_found(session, client, test_projects):
    url = project_url + str(100)

    res = client.get(url)

    assert res.status_code == status.HTTP_404_NOT_FOUND


def test_update_project(session, client, user_cred, test_projects):
    url = project_url + str(test_projects[0].id)

    data = {
        "name": "test_project_updated",
        "description": "test_description_updated",
        "project_type": "COMMUNITY",
        "project_priority": "MEDIUM PRIORITY",
        # "project_tools": [68, 25],
        "manager_id": 1
    }

    res = client.put(url, json=data, headers={"Authorization": f"{user_cred.token_type} {user_cred.token}"})
    res_data = res.json()

    assert res.status_code == status.HTTP_201_CREATED
    assert res_data['name'] == data['name']


def test_update_project_does_not_exist(session, client, user_cred, test_projects):
    url = project_url + str(100)

    data = {
        "name": "test_project_updated",
        "description": "test_description_updated",
        "project_type": "COMMUNITY",
        "project_priority": "MEDIUM PRIORITY",
        # "project_tools": [68, 25],
        "manager_id": 1
    }

    res = client.put(url, json=data, headers={"Authorization": f"{user_cred.token_type} {user_cred.token}"})

    assert res.status_code == status.HTTP_404_NOT_FOUND


def test_update_project_not_authorized(client, test_projects):
    url = project_url + str(test_projects[0].id)

    data = {
        "name": "test_project_updated",
        "description": "test_description_updated",
        "project_type": "COMMUNITY",
        "project_priority": "MEDIUM PRIORITY",
        # "project_tools": [68, 25],
        "manager_id": 1
    }

    res = client.put(url, json=data)

    assert res.status_code == status.HTTP_401_UNAUTHORIZED


def test_delete_project(session, client, user_cred, test_projects):
    url = project_url + str(test_projects[0].id)

    res = client.delete(url, headers={"Authorization": f"{user_cred.token_type} {user_cred.token}"})

    assert res.status_code == status.HTTP_204_NO_CONTENT


def test_delete_project_does_not_exist(session, client, user_cred, test_projects):
    url = project_url + str(100)

    res = client.delete(url, headers={"Authorization": f"{user_cred.token_type} {user_cred.token}"})

    assert res.status_code == status.HTTP_404_NOT_FOUND


def test_delete_project_unauthorized(client, test_projects):
    url = project_url + str(test_projects[0].id)

    res = client.delete(url)

    assert res.status_code == status.HTTP_401_UNAUTHORIZED


def test_add_user_project(client, test_projects, user_cred, test_user1):
    url = project_url + str(test_projects[0].id) + "/add/" + str(test_user1["id"])
    data = {
        "team": "FRONTEND"
    }
    res = client.post(url, json=data, headers={"Authorization": f"{user_cred.token_type} {user_cred.token}"})

    assert res.status_code == status.HTTP_201_CREATED


def test_add_user_project_unauthorized(client, test_projects, test_user, user_cred):
    url = project_url + str(test_projects[2].id) + "/add/" + str(test_user["id"])
    data = {
        "team": "FRONTEND"
    }
    res = client.post(url, json=data, headers={"Authorization": f"{user_cred.token_type} {user_cred.token}"})

    assert res.status_code == status.HTTP_403_FORBIDDEN


def test_add_user_does_not_exist(client, test_projects, user_cred, test_user1):
    url = project_url + str(test_projects[0].id) + "/add/" + str(100)
    data = {
        "team": "DESIGNER"
    }
    res = client.post(url, json=data, headers={"Authorization": f"{user_cred.token_type} {user_cred.token}"})

    assert res.status_code == status.HTTP_404_NOT_FOUND


def test_add_user_already_exists(client, test_projects, user_cred, test_user1):
    test_add_user_project(client, test_projects, user_cred, test_user1)
    url = project_url + str(test_projects[0].id) + "/add/" + str(test_user1["id"])
    data = {
        "team": "MOBILE"
    }
    res = client.post(url, json=data, headers={"Authorization": f"{user_cred.token_type} {user_cred.token}"})

    assert res.status_code == status.HTTP_400_BAD_REQUEST


def test_remove_user_project(client, test_projects, user_cred, test_user1):
    test_add_user_project(client, test_projects, user_cred, test_user1)
    url = project_url + str(test_projects[0].id) + "/remove/" + str(test_user1["id"])

    res = client.delete(url, headers={"Authorization": f"{user_cred.token_type} {user_cred.token}"})

    assert res.status_code == status.HTTP_204_NO_CONTENT


def test_remove_user_project_unauthorized(client, test_projects, test_user, user_cred):
    url = project_url + str(test_projects[2].id) + "/remove/" + str(test_user["id"])

    res = client.delete(url, headers={"Authorization": f"{user_cred.token_type} {user_cred.token}"})

    assert res.status_code == status.HTTP_403_FORBIDDEN


def test_get_all_team_members(client, user_cred, test_user1, test_projects):
    test_add_user_project(client, test_projects, user_cred, test_user1)
    url = project_url + str(1) + "/members?team=FRONTEND"
    res = client.get(url)
    members = res.json()

    assert res.status_code == 200
    assert len(members) == 1
