import pytest
from fastapi import status
from app import app
from db.models.stacks import Stack



# Factory to create stacks
@pytest.fixture
def stack_factory(session):
	def create_stack(name):
		stack = Stack(name=name)

		session.add(stack)
		session.commit()
		session.refresh(stack)

		return stack

	return create_stack



def test_list_stacks(session, client, stack_factory):
	url = app.url_path_for("list_stacks")

	# list of stack names
	stack_names = ["backend", "frontend"]
	for stack in stack_names:
		stack_factory(stack)

	res = client.get(url)
	res_data = res.json()

	assert res.status_code == status.HTTP_200_OK
	assert len(res_data) == 2


def test_create_stack(session, client, user_cred):
	url = app.url_path_for("create_stack")

	data = {"name": "backend"}

	res = client.post(url, json=data, headers={"Authorization": f"{user_cred.token_type} {user_cred.token}"})
	res_data = res.json()

	assert res.status_code == status.HTTP_201_CREATED
	assert res_data['name'] == data['name']


def test_create_stack_no_user(session, client):
	url = app.url_path_for("create_stack")

	data = {"name": "backend"}, 
	res = client.post(url, json=data)

	assert res.status_code == status.HTTP_401_UNAUTHORIZED
	


def test_read_stack(session, client, stack_factory):
	# create stack
	stack = stack_factory("backend")

	url = app.url_path_for("read_stack", stack_id=stack.id)
	res = client.get(url)
	res_data = res.json()

	assert res.status_code == status.HTTP_200_OK
	assert res_data['name'] == stack.name


def test_update_stack(session, client, user_cred, stack_factory):
	# create stack
	stack = stack_factory("backend")

	data = {"name": "frontend"}

	url = app.url_path_for("update_stack", stack_id=stack.id)
	res = client.patch(url, json=data, headers={"Authorization": f"{user_cred.token_type} {user_cred.token}"})
	res_data = res.json()

	assert res.status_code == status.HTTP_200_OK
	assert res_data['name'] == data['name']



def test_delete_stack(session, client, user_cred, stack_factory):
	# create stack
	stack = stack_factory("backend")

	url = app.url_path_for("delete_stack", stack_id=stack.id)
	res = client.delete(url, headers={"Authorization": f"{user_cred.token_type} {user_cred.token}"})

	assert res.status_code == status.HTTP_204_NO_CONTENT


def test_duplicate_stack(session, client, user_cred, stack_factory):
	stack = stack_factory("backend")
	url = app.url_path_for("create_stack")

	data = {"name": "backend"}

	res = client.post(url, json=data, headers={"Authorization": f"{user_cred.token_type} {user_cred.token}"})

	assert res.status_code == status.HTTP_400_BAD_REQUEST


