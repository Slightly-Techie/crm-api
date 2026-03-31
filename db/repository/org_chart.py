from typing import Optional

from sqlalchemy import literal, select
# from sqlalchemy.orm import Session

from db.models.users import User
from db.repository.base import BaseRepository
from utils.enums import UserStatus


class OrgChartRepository(BaseRepository):
    model = User

    def get_user(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_direct_subordinates(self, user_id: int) -> list[User]:
        return (
            self.db.query(User)
            .filter(User.manager_id == user_id, User.status == UserStatus.ACCEPTED)
            .all()
        )

    def get_subtree_ids(self, root_id: int, max_depth: int = 5) -> list[dict]:
        """Fetch all descendant user IDs using a recursive CTE, up to max_depth.

        Returns a list of dicts: [{"id": ..., "manager_id": ..., "depth": ...}]
        """
        # Anchor: the root user at depth 0 (only accepted users)
        anchor = (
            select(
                User.id,
                User.manager_id,
                literal(0).label("depth"),
            )
            .where(User.id == root_id, User.status == UserStatus.ACCEPTED)
            .cte(name="org_tree", recursive=True)
        )

        # Recursive member: children of current level, depth + 1 (only accepted)
        recursive = (
            select(
                User.id,
                User.manager_id,
                (anchor.c.depth + 1).label("depth"),
            )
            .join(anchor, User.manager_id == anchor.c.id)
            .where(anchor.c.depth < max_depth, User.status == UserStatus.ACCEPTED)
        )

        cte = anchor.union_all(recursive)

        rows = self.db.execute(select(cte.c.id, cte.c.manager_id, cte.c.depth)).all()
        return [{"id": r.id, "manager_id": r.manager_id, "depth": r.depth} for r in rows]

    def get_users_by_ids(self, user_ids: list[int]) -> list[User]:
        """Fetch full User objects for a list of IDs in a single query."""
        if not user_ids:
            return []
        return self.db.query(User).filter(User.id.in_(user_ids)).all()

    def get_root_users(self) -> list[User]:
        """Return accepted users with no manager (org tree roots)."""
        return (
            self.db.query(User)
            .filter(User.manager_id.is_(None), User.status == UserStatus.ACCEPTED)
            .all()
        )

    def get_ancestor_ids(self, user_id: int, max_depth: int = 50) -> list[int]:
        """Walk the manager chain upward using a recursive CTE.

        Returns a list of ancestor user IDs (excluding the starting user),
        ordered from immediate manager to the root.
        Used for circular-reference detection.
        """
        anchor = (
            select(
                User.id,
                User.manager_id,
                literal(0).label("depth"),
            )
            .where(User.id == user_id)
            .cte(name="ancestors", recursive=True)
        )

        recursive = (
            select(
                User.id,
                User.manager_id,
                (anchor.c.depth + 1).label("depth"),
            )
            .join(anchor, User.id == anchor.c.manager_id)
            .where(anchor.c.depth < max_depth)
        )

        cte = anchor.union_all(recursive)

        rows = self.db.execute(
            select(cte.c.id).where(cte.c.depth > 0).order_by(cte.c.depth)
        ).all()
        return [r.id for r in rows]

    def set_manager(self, user: User, manager_id: Optional[int]) -> User:
        user.manager_id = manager_id
        self.db.commit()
        self.db.refresh(user)
        return user

    def bulk_set_manager(self, users: list[User], manager_id: int) -> list[User]:
        for user in users:
            user.manager_id = manager_id
        self.db.commit()
        for user in users:
            self.db.refresh(user)
        return users

    def reassign_subordinates(self, user: User) -> None:
        """Reassign all direct subordinates of `user` to `user.manager_id`.

        If the user has no manager, subordinates become roots (manager_id=NULL).
        """
        subordinates = self.get_direct_subordinates(user.id)
        for sub in subordinates:
            sub.manager_id = user.manager_id
        if subordinates:
            self.db.flush()

    def delete_user(self, user: User) -> None:
        """Delete a user after reassigning subordinates."""
        self.reassign_subordinates(user)
        self.db.delete(user)
        self.db.commit()
