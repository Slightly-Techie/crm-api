"""
GET  /users/{user_id}/subordinates     – direct reports of a user
GET  /users/{user_id}/org-chart        – full subtree rooted at a user
PATCH /users/{user_id}/manager         – assign / remove a user's manager
GET  /org-chart                        – the full organisational tree (all roots)
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.api_models.user import OrgChartNode, SubordinateResponse, UpdateManagerRequest
from db.database import get_db
from db.models.users import User
from utils.oauth2 import get_current_user
from utils.permissions import is_admin

users_route = APIRouter(tags=["Org Chart"], prefix="/users")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_user_or_404(user_id: int, db: Session) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found",
        )
    return user


def _build_org_chart_node(user: User) -> OrgChartNode:
    """Recursively build an OrgChartNode from a User ORM object.

    SQLAlchemy's adjacency-list ``subordinates`` relationship is already
    loaded (lazy by default), so this traverses the in-session graph.
    """
    return OrgChartNode(
        id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        username=user.username,
        profile_pic_url=user.profile_pic_url,
        role=user.role,
        stack=user.stack,
        manager_id=user.manager_id,
        subordinates=[_build_org_chart_node(sub) for sub in user.subordinates],
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@users_route.get(
    "/{user_id}/subordinates",
    response_model=list[SubordinateResponse],
    summary="Get direct reports of a user",
)
def get_subordinates(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return the **immediate** direct reports of the given user."""
    user = _get_user_or_404(user_id, db)
    return user.subordinates


@users_route.get(
    "/{user_id}/org-chart",
    response_model=OrgChartNode,
    summary="Get full reporting subtree rooted at a user",
)
def get_user_org_chart(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return the user as the root of a recursive org-chart tree containing
    all subordinates at every depth."""
    user = _get_user_or_404(user_id, db)
    return _build_org_chart_node(user)


@users_route.patch(
    "/{user_id}/manager",
    response_model=SubordinateResponse,
    summary="Assign or remove a user's manager",
)
def update_manager(
    user_id: int,
    payload: UpdateManagerRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(is_admin),
):
    """Set or clear ``manager_id`` for a user.

    * Pass ``manager_id: <int>`` to assign a manager.
    * Pass ``manager_id: null`` to remove the current manager relationship.

    Prevents circular references: a user cannot be set as their own manager,
    and the proposed manager must not already report (directly or indirectly)
    to the target user.
    """
    user = _get_user_or_404(user_id, db)

    if payload.manager_id is not None:
        if payload.manager_id == user_id:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="A user cannot be their own manager.",
            )

        new_manager = _get_user_or_404(payload.manager_id, db)

        # Circular-reference guard: walk up the proposed manager's chain and
        # make sure we never encounter the target user.
        from typing import Optional as _Opt
        current_ancestor: _Opt[User] = new_manager
        visited: set[int] = set()
        while current_ancestor is not None and current_ancestor.manager_id is not None:
            next_manager_id: int = current_ancestor.manager_id
            if next_manager_id in visited:
                break  # already-circular chain in data – stop gracefully
            visited.add(next_manager_id)
            if next_manager_id == user_id:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=(
                        f"Circular reference detected: user {payload.manager_id} "
                        f"already reports (directly or indirectly) to user {user_id}."
                    ),
                )
            current_ancestor = db.query(User).filter(User.id == next_manager_id).first()

    user.manager_id = payload.manager_id
    db.commit()
    db.refresh(user)
    return user


@users_route.get(
    "/org-chart",
    response_model=list[OrgChartNode],
    summary="Get the complete organisational tree",
)
def get_full_org_chart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return the entire org chart as a forest (list of root nodes).

    Root nodes are users whose ``manager_id`` is NULL (i.e. they have no
    manager — typically the CEO / co-founders).
    """
    roots = db.query(User).filter(User.manager_id.is_(None)).all()
    return [_build_org_chart_node(root) for root in roots]
