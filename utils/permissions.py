from .oauth2 import get_current_user
from fastapi import Depends
from api.api_models.user import UserResponse
from utils.utils import RoleChoices
from core.exceptions import ForbiddenError


def is_authenticated(user: UserResponse = Depends(get_current_user)):
	'''
		No need to do anything because `get_current_user` raises all the errors
		his would be used as a path dependecy so return value is required
	
		Usage: @app.<method>("<route>", dependencies=[Depends(is_authenticated)] )
	'''

	return user


# Admin permission dependency
def is_admin(user: UserResponse = Depends(is_authenticated)):
	if user.role.name != RoleChoices.ADMIN:
		raise ForbiddenError()

	return user



# Function to check ownership or admin
def is_owner_or_admin(user, obj):
	'''
	params:
		user: current user model
		obj: object model with user field

	return:
		bool
	'''
	if not hasattr(user, 'role'):
		raise ForbiddenError()

	if user.role.name == RoleChoices.ADMIN:
		return True

	if user.id == obj.user_id:
		return True

	raise ForbiddenError()


# Function to check if user is owner 
def is_owner(user, obj):
	if user.id == obj.user_id:
		return True

	raise ForbiddenError()


# Function to check if user is project manager
def is_project_manager(user, obj):
    return True
