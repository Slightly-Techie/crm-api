from .oauth2 import get_current_user
from fastapi import Depends
from api.api_models.user import UserResponse
from utils.utils import RoleEnum
from core.exceptions import ForbiddenError

# Admin permission dependency
def admin_permission(user: UserResponse = Depends(get_current_user)):
	if user.role.name != RoleEnum.ADMIN:
		raise ForbiddenError()


# Manager permission dependency
def manager_permission(user: UserResponse = Depends(get_current_user)):
	if user.role.name != RoleEnum.MANAGER:
		raise ForbiddenError()


def is_authenticated(user: UserResponse = Depends(get_current_user)):
	# No need to do anything because `get_current_user` raises all the errors
	# This would be used as a path dependecy so return value is required
	#
	# Usage: @app.<method>("<route>", dependencies=[Depends(is_authenticated)] )

	pass
