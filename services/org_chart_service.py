from typing import Optional

from fastapi import HTTPException, status

from api.api_models.user import OrgChartNode
from db.models.users import User
from db.repository.org_chart import OrgChartRepository


class OrgChartService:
    DEFAULT_MAX_DEPTH = 5

    def __init__(self, repo: OrgChartRepository):
        self.repo = repo

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _get_user_or_404(self, user_id: int) -> User:
        user = self.repo.get_user(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found",
            )
        return user

    @staticmethod
    def _build_tree(users_by_id: dict[int, User], root_id: int, rows: list[dict]) -> OrgChartNode:
        """Assemble an OrgChartNode tree from flat CTE rows.

        Each row has {"id", "manager_id", "depth"}. We build a parent→children
        map, then recurse from the root.
        """
        children_map: dict[int, list[int]] = {}
        for row in rows:
            pid = row["manager_id"]
            if pid is not None and pid in users_by_id:
                children_map.setdefault(pid, []).append(row["id"])

        visited: set[int] = set()

        def _recurse(uid: int) -> Optional[OrgChartNode]:
            if uid in visited or uid not in users_by_id:
                return None
            visited.add(uid)
            u = users_by_id[uid]
            child_ids = children_map.get(uid, [])
            subs = []
            for cid in child_ids:
                node = _recurse(cid)
                if node is not None:
                    subs.append(node)
            return OrgChartNode(
                id=u.id,
                first_name=u.first_name,
                last_name=u.last_name,
                username=u.username,
                profile_pic_url=u.profile_pic_url,
                role=u.role,
                stack=u.stack,
                manager_id=u.manager_id,
                subordinates=subs,
            )

        node = _recurse(root_id)
        if node is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {root_id} not found",
            )
        return node

    # ------------------------------------------------------------------
    # Read operations
    # ------------------------------------------------------------------

    def get_direct_subordinates(self, user_id: int) -> list[User]:
        self._get_user_or_404(user_id)
        return self.repo.get_direct_subordinates(user_id)

    def get_subtree(self, root_id: int, max_depth: Optional[int] = None) -> OrgChartNode:
        max_depth = max_depth if max_depth is not None else self.DEFAULT_MAX_DEPTH
        self._get_user_or_404(root_id)
        rows = self.repo.get_subtree_ids(root_id, max_depth)
        user_ids = [r["id"] for r in rows]
        users = self.repo.get_users_by_ids(user_ids)
        users_by_id = {u.id: u for u in users}
        return self._build_tree(users_by_id, root_id, rows)

    def get_full_org_chart(self, max_depth: Optional[int] = None) -> list[OrgChartNode]:
        max_depth = max_depth if max_depth is not None else self.DEFAULT_MAX_DEPTH
        roots = self.repo.get_root_users()
        if not roots:
            return []
        result = []
        for root in roots:
            rows = self.repo.get_subtree_ids(root.id, max_depth)
            user_ids = [r["id"] for r in rows]
            users = self.repo.get_users_by_ids(user_ids)
            users_by_id = {u.id: u for u in users}
            result.append(self._build_tree(users_by_id, root.id, rows))
        return result

    def get_manager(self, user_id: int) -> Optional[User]:
        user = self._get_user_or_404(user_id)
        if user.manager_id is None:
            return None
        return self.repo.get_user(user.manager_id)

    # ------------------------------------------------------------------
    # Write operations
    # ------------------------------------------------------------------

    def update_manager(self, user_id: int, manager_id: Optional[int]) -> User:
        user = self._get_user_or_404(user_id)

        if manager_id is None:
            return self.repo.set_manager(user, None)

        if manager_id == user_id:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="A user cannot be their own manager.",
            )

        # Validate manager exists
        self._get_user_or_404(manager_id)

        # Circular-reference guard via recursive CTE (single query)
        ancestor_ids = self.repo.get_ancestor_ids(manager_id)
        if user_id in ancestor_ids:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    f"Circular reference detected: user {manager_id} "
                    f"already reports (directly or indirectly) to user {user_id}."
                ),
            )

        return self.repo.set_manager(user, manager_id)

    def bulk_assign_subordinates(self, manager_id: int, user_ids: list[int]) -> dict:
        _ = self._get_user_or_404(manager_id)

        if manager_id in user_ids:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="A user cannot be their own subordinate.",
            )

        # Check for circular references: the manager must not already
        # report (directly or indirectly) to any of the proposed subordinates.
        manager_ancestor_ids = set(self.repo.get_ancestor_ids(manager_id))
        for uid in user_ids:
            if uid in manager_ancestor_ids:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=(
                        f"Circular reference detected: user {manager_id} "
                        f"already reports (directly or indirectly) to user {uid}."
                    ),
                )

        found_users = self.repo.get_users_by_ids(user_ids)
        found_ids = {u.id for u in found_users}
        not_found = [uid for uid in user_ids if uid not in found_ids]

        if found_users:
            self.repo.bulk_set_manager(found_users, manager_id)

        return {"updated": found_users, "not_found": not_found}

    def delete_user(self, user_id: int) -> None:
        """Delete a user, reassigning their subordinates to their manager."""
        user = self._get_user_or_404(user_id)
        self.repo.delete_user(user)
