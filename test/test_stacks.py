import pytest
from fastapi import status
from app import app
from db.models.users import Stack

from .test_users import test_log_in



@pytest.fixture
def stack_factory(session):
	def create_stack(name):
		stack = Stack(name=name)

		session.add(stack)
		session.commit()
		session.refresh(stack)

		return stack

	return create_stack




def test_list_stacks(session, client, test_user, stack_factory):
	url = app.url_parth_for("read_stacks")

	# login response
	login_res = test_log_in(client, test_user)

	# list of stack names
	stack_names = ["backend", "frontend"]
	for stack in stack_names:
		stack_factory(name)


	res = client.get(url, headers={"Authorization": f"{login_res.token_type} {login_res.token}"})

	assert res.status_code == status.HTTP_200_OK



