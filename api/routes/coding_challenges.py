from fastapi import APIRouter, Depends, status
from fastapi_pagination.ext.sqlalchemy import paginate
from fastapi_pagination.links import Page
from sqlalchemy.orm import Session

from api.api_models.coding_challenges import (
    CodingChallengeCreate,
    CodingChallengeResponse,
    CodingChallengeUpdate
)
from db.database import get_db
from db.repository.coding_challenges import CodingChallengeRepository
from services.coding_challenge_service import CodingChallengeService
from utils.permissions import is_admin, user_accepted

coding_challenge_route = APIRouter(tags=["Coding Challenges"], prefix="/coding-challenges")


def _service(db: Session) -> CodingChallengeService:
    return CodingChallengeService(CodingChallengeRepository(db))


@coding_challenge_route.post("/", status_code=status.HTTP_201_CREATED, response_model=CodingChallengeResponse)
def create_challenge(
    challenge: CodingChallengeCreate,
    current_user=Depends(is_admin),
    db: Session = Depends(get_db)
):
    """Create a new coding challenge - Admin only"""
    return _service(db).create(challenge.model_dump(), current_user.id)


@coding_challenge_route.get("/latest", status_code=status.HTTP_200_OK, response_model=CodingChallengeResponse | None)
def get_latest_challenge(db: Session = Depends(get_db), current_user=Depends(user_accepted)):
    """Get the most recent coding challenge - Accepted users"""
    return _service(db).get_latest()


@coding_challenge_route.get("/", status_code=status.HTTP_200_OK, response_model=Page[CodingChallengeResponse])
def get_all_challenges(db: Session = Depends(get_db), current_user=Depends(user_accepted)):
    """Get all coding challenges - Accepted users"""
    return paginate(db, _service(db).get_all_query())


@coding_challenge_route.get("/{challenge_id}", status_code=status.HTTP_200_OK, response_model=CodingChallengeResponse)
def get_challenge_by_id(
    challenge_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(user_accepted)
):
    """Get a specific challenge by ID"""
    return _service(db).get_by_id(challenge_id)


@coding_challenge_route.put("/{challenge_id}", status_code=status.HTTP_200_OK, response_model=CodingChallengeResponse)
def update_challenge(
    challenge_id: int,
    challenge: CodingChallengeUpdate,
    current_user=Depends(is_admin),
    db: Session = Depends(get_db)
):
    """Update a challenge - Admin only"""
    return _service(db).update(challenge_id, challenge.model_dump(exclude_unset=True))


@coding_challenge_route.delete("/{challenge_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_challenge(
    challenge_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(is_admin)
):
    """Delete a challenge - Admin only"""
    _service(db).delete(challenge_id)
