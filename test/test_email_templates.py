import pytest

from api.api_models.user import UserResponse
from db.models.email_template import EmailTemplate
from utils.enums import EmailTemplateName


def test_get_all_email_templates(client, test_email_templates, test_user):
    login_res = client.post(
        "/api/v1/users/login", data={"username": test_user["email"], "password": test_user["password"]})
    token = login_res.json()["token"]

    response = client.get("/api/v1/email-templates/",headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == len(test_email_templates)

def test_create_email_template( client, test_user):
    login_res = client.post(
        "/api/v1/users/login", data={"username": test_user["email"], "password": test_user["password"]})
    token = login_res.json()["token"]

    response = client.post(
        "/api/v1/email-templates/",
        json={"template_name": EmailTemplateName.ACCEPTED,"subject":"Welcome to Slightly Techie!", "html_content": "<div>New Content</div>"},
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["template_name"] == EmailTemplateName.ACCEPTED
    assert "<div>New Content</div>" in data["html_content"]


def test_get_email_template(client, test_email_templates, test_user):
    login_res = client.post(
        "/api/v1/users/login", data={"username": test_user["email"], "password": test_user["password"]})
    token = login_res.json()["token"]

    template_id = test_email_templates[0].id
    response = client.get(f"/api/v1/email-templates/{template_id}",headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == template_id
    assert data["template_name"] == test_email_templates[0].template_name


def test_update_email_template(client, test_email_templates,test_user):
    login_res = client.post(
        "/api/v1/users/login", data={"username": test_user["email"], "password": test_user["password"]})
    token = login_res.json()["token"]

    template_id = test_email_templates[0].id
    response = client.put(
        f"/api/v1/email-templates/{template_id}",headers={'Authorization': f'Bearer {token}'},
        json={"template_name": EmailTemplateName.ACCEPTED,"subject":"Welcome to Slightly Techie!", "html_content": "<div>Updated Content</div>"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["template_name"] == EmailTemplateName.ACCEPTED
    assert "<div>Updated Content</div>" in data["html_content"]

def test_delete_email_template(client, test_email_templates, test_user):
    login_res = client.post(
        "/api/v1/users/login", data={"username": test_user["email"], "password": test_user["password"]})

    template_id = test_email_templates[1].id
    token = login_res.json()["token"]

    response = client.delete(f"/api/v1/email-templates/{template_id}",headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 204

    response = client.get(f"/api/v1/email-templates/{template_id}")
    assert response.status_code == 404
