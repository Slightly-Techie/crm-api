"""
Org-chart endpoints.

**Admin-only** (write / destructive operations):
    PATCH /users/{user_id}/manager       – assign / remove a user's manager
    GET  /users/{user_id}/manager        – manager of any user (admin)
    GET  /users/{user_id}/subordinates   – direct reports of any user (admin)
    GET  /users/{user_id}/org-chart      – full subtree rooted at any user (admin)

**Authenticated accepted users** (read-only):
  GET  /users/org-chart                – complete organisational tree
  GET  /users/me/manager               – my manager
  GET  /users/me/subordinates          – my direct reports
    GET  /users/view/{user_id}/manager        – manager of any user
    GET  /users/view/{user_id}/subordinates   – direct reports of any user
    GET  /users/view/{user_id}/org-chart      – full subtree rooted at any user
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from api.api_models.user import (
    BulkAssignSubordinatesRequest,
    BulkAssignSubordinatesResponse,
    ManagerInfo,
    OrgChartNode,
    SubordinateResponse,
    UpdateManagerRequest,
)
from db.database import get_db
from db.repository.org_chart import OrgChartRepository
from services.org_chart_service import OrgChartService
from utils.permissions import is_admin, user_accepted

users_route = APIRouter(tags=["Org Chart"], prefix="/users")


def _get_service(db: Session = Depends(get_db)) -> OrgChartService:
    return OrgChartService(OrgChartRepository(db))


# ---------------------------------------------------------------------------
# Self-scoped endpoints (accepted users)
# ---------------------------------------------------------------------------

@users_route.get(
    "/me/manager",
    response_model=Optional[ManagerInfo],
    summary="Get my manager",
)
def get_my_manager(
    current_user=Depends(user_accepted),
    service: OrgChartService = Depends(_get_service),
):
    manager = service.get_manager(current_user.id)
    return manager


@users_route.get(
    "/me/subordinates",
    response_model=list[SubordinateResponse],
    summary="Get my direct reports",
)
def get_my_subordinates(
    current_user=Depends(user_accepted),
    service: OrgChartService = Depends(_get_service),
):
    return service.get_direct_subordinates(current_user.id)


# ---------------------------------------------------------------------------
# Admin endpoints — static routes BEFORE parameterised ones
# ---------------------------------------------------------------------------

@users_route.get(
    "/org-chart",
    response_model=list[OrgChartNode],
    summary="Get the complete organisational tree",
)
def get_full_org_chart(
    max_depth: int = Query(default=5, ge=1, le=20),
    current_user=Depends(user_accepted),
    service: OrgChartService = Depends(_get_service),
):
    return service.get_full_org_chart(max_depth)


@users_route.post(
    "/assign-subordinates",
    response_model=BulkAssignSubordinatesResponse,
    summary="Bulk assign subordinates to a manager",
)
def bulk_assign_subordinates(
    payload: BulkAssignSubordinatesRequest,
    manager_id: int = Query(..., description="The user ID of the manager"),
    current_user=Depends(is_admin),
    service: OrgChartService = Depends(_get_service),
):
    """Assign multiple users as subordinates of a given manager in one call."""
    return service.bulk_assign_subordinates(manager_id, payload.user_ids)


# ---------------------------------------------------------------------------
# Accepted-user read-only view endpoints
# ---------------------------------------------------------------------------

@users_route.get(
    "/view/{user_id}/manager",
    response_model=Optional[ManagerInfo],
    summary="View manager of a user",
)
def view_user_manager(
    user_id: int,
    current_user=Depends(user_accepted),
    service: OrgChartService = Depends(_get_service),
):
    return service.get_manager(user_id)


@users_route.get(
    "/view/{user_id}/subordinates",
    response_model=list[SubordinateResponse],
    summary="View direct reports of a user",
)
def view_subordinates(
    user_id: int,
    current_user=Depends(user_accepted),
    service: OrgChartService = Depends(_get_service),
):
    return service.get_direct_subordinates(user_id)


@users_route.get(
    "/view/{user_id}/org-chart",
    response_model=OrgChartNode,
    summary="View full reporting subtree rooted at a user",
)
def view_user_org_chart(
    user_id: int,
    max_depth: int = Query(default=5, ge=1, le=20),
    current_user=Depends(user_accepted),
    service: OrgChartService = Depends(_get_service),
):
    return service.get_subtree(user_id, max_depth)


# ---------------------------------------------------------------------------
# Admin endpoints — parameterised
# ---------------------------------------------------------------------------

@users_route.get(
    "/{user_id}/manager",
    response_model=Optional[ManagerInfo],
    summary="Get manager of a user",
)
def get_user_manager(
    user_id: int,
    current_user=Depends(is_admin),
    service: OrgChartService = Depends(_get_service),
):
    return service.get_manager(user_id)


@users_route.get(
    "/{user_id}/subordinates",
    response_model=list[SubordinateResponse],
    summary="Get direct reports of a user",
)
def get_subordinates(
    user_id: int,
    current_user=Depends(is_admin),
    service: OrgChartService = Depends(_get_service),
):
    return service.get_direct_subordinates(user_id)


@users_route.get(
    "/{user_id}/org-chart",
    response_model=OrgChartNode,
    summary="Get full reporting subtree rooted at a user",
)
def get_user_org_chart(
    user_id: int,
    max_depth: int = Query(default=5, ge=1, le=20),
    current_user=Depends(is_admin),
    service: OrgChartService = Depends(_get_service),
):
    return service.get_subtree(user_id, max_depth)


@users_route.patch(
    "/{user_id}/manager",
    response_model=SubordinateResponse,
    summary="Assign or remove a user's manager",
)
def update_manager(
    user_id: int,
    payload: UpdateManagerRequest,
    current_user=Depends(is_admin),
    service: OrgChartService = Depends(_get_service),
):
    """Set or clear ``manager_id`` for a user.

    * Pass ``manager_id: <int>`` to assign a manager.
    * Pass ``manager_id: null`` to remove the current manager.
    """
    return service.update_manager(user_id, payload.manager_id)


@users_route.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a user and reassign their subordinates",
)
def delete_user(
    user_id: int,
    current_user=Depends(is_admin),
    service: OrgChartService = Depends(_get_service),
):
    """Delete a user. Their subordinates are reassigned to the deleted user's
    manager. If the deleted user had no manager, subordinates become roots."""
    service.delete_user(user_id)
