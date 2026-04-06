import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Query, UploadFile, status
from fastapi_pagination.ext.sqlalchemy import paginate
from fastapi_pagination.links import Page
from pydantic import BaseModel
from sqlalchemy.orm import Session

from api.api_models.user import ApplicantProfileResponse, ProfileResponse, ProfileUpdate
from utils.enums import UserStatus


class BatchStatusUpdateRequest(BaseModel):
    user_ids: List[int]
    status: UserStatus


class BatchStatusUpdateResponse(BaseModel):
    updated_count: int
    updated_users: List[ProfileResponse]
    failed_ids: List[int]
from db.database import get_db
from db.models.users import User
from db.repository.email_templates import EmailTemplateRepository
from db.repository.technical_tasks import TechnicalTaskSubmissionRepository
from db.repository.users import UserRepository
from services.user_service import UserService
from utils.permissions import is_admin, user_accepted

profile_route = APIRouter(tags=["User"], prefix="/users")
logger = logging.getLogger(__name__)


def _service(db: Session) -> UserService:
    return UserService(
        UserRepository(db),
        EmailTemplateRepository(db),
        TechnicalTaskSubmissionRepository(db)
    )


@profile_route.get("/profile/{user_id}", response_model=ApplicantProfileResponse)
async def get_profile(user_id: int, db: Session = Depends(get_db),
                      current_user: User = Depends(user_accepted)):
    return _service(db).get_profile(user_id)


@profile_route.put("/profile", response_model=ProfileResponse)
async def update_profile(userDetails: ProfileUpdate, current_user: User = Depends(user_accepted),
                         db: Session = Depends(get_db)):
    return _service(db).update_profile(current_user.id, userDetails.model_dump(exclude_unset=True))


@profile_route.get("/", response_model=Page[ProfileResponse])
def get_all_profile(skill: str = Query(None), stack: str = Query(None),
                    active: Optional[bool] = None, p: Optional[str] = None,
                    status: Optional[UserStatus] = Query(
                        None,
                        description="Filter users by status. Accepted values are defined by the UserStatus enum."
                    ),
                    db: Session = Depends(get_db), current_user: User = Depends(user_accepted)):
    query = _service(db).build_search_query(
        skill,
        stack,
        active,
        p,
        status.value if status is not None else None
    )
    return paginate(db, query)


@profile_route.put("/profile/{user_id}/activate", response_model=ProfileResponse,
                   status_code=status.HTTP_200_OK)
def update_profile_status(user_id: int, db: Session = Depends(get_db),
                          current_user: User = Depends(is_admin)):
    return _service(db).activate_user(user_id)


@profile_route.get("/user_info", response_model=dict)
def get_user_info(email: str, db: Session = Depends(get_db),
                  current_user: User = Depends(user_accepted)):
    return _service(db).get_user_info(email)


@profile_route.put("/profile/{user_id}/status", response_model=ProfileResponse,
                   status_code=status.HTTP_200_OK)
async def update_user_status(user_id: int, new_status: UserStatus, db: Session = Depends(get_db),
                             current_user: User = Depends(is_admin)):
    return await _service(db).update_user_status(user_id, new_status)


@profile_route.patch("/profile/avatar", response_model=ProfileResponse,
                     status_code=status.HTTP_200_OK)
async def update_avi(current_user: User = Depends(user_accepted),
                     db: Session = Depends(get_db), file: UploadFile = File(...)):
    return await _service(db).update_avatar(current_user, file)


@profile_route.post("/batch/status", response_model=BatchStatusUpdateResponse,
                    status_code=status.HTTP_200_OK)
async def batch_update_status(
    request: BatchStatusUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(is_admin)
):
    """Batch update user statuses - Admin only"""
    updated_users = []
    failed_ids = []

    for user_id in request.user_ids:
        try:
            updated_user = await _service(db).update_user_status(user_id, request.status)
            updated_users.append(updated_user)
        except Exception:
            logger.exception("Failed to update user status in batch", extra={"user_id": user_id})
            failed_ids.append(user_id)

    return BatchStatusUpdateResponse(
        updated_count=len(updated_users),
        updated_users=updated_users,
        failed_ids=failed_ids
    )
