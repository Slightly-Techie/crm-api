from typing import Optional

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from api.api_models.user import UserSignUp
from db.models.users import User
from db.models.skills import Skill
from db.models import users_skills
from db.repository.base import BaseRepository


class UserRepository(BaseRepository):
    model = User

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def get_by_username(self, username: str) -> Optional[User]:
        return self.db.query(User).filter(User.username == username).first()

    def create(self, user_data: UserSignUp) -> User:
        from db.models.roles import Role
        from utils.utils import RoleChoices

        data = user_data.model_dump().copy()
        data.pop("password_confirmation")

        # Ensure role_id is set - default to USER role if not provided
        if not data.get("role_id"):
            user_role = self.db.query(Role).filter(Role.name == RoleChoices.USER).first()
            if user_role:
                data["role_id"] = user_role.id

        new_user = User(**data)
        return self.save(new_user)

    def update_by_id(self, user_id: int, update_data: dict) -> Optional[User]:
        query = self.db.query(User).filter(User.id == user_id)
        query.update(update_data)
        self.db.commit()
        return query.first()

    def update_status(self, user: User, new_status) -> User:
        user.status = new_status
        self.db.commit()
        self.db.refresh(user)
        return user

    def activate(self, user: User) -> User:
        user.is_active = True
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_password(self, user: User, hashed_password: str) -> User:
        user.password = hashed_password
        self.db.commit()
        return user

    def update_avatar(self, user: User, url: str) -> User:
        user.profile_pic_url = url
        self.db.commit()
        self.db.refresh(user)
        return user

    def build_search_query(self, skill: Optional[str], stack: Optional[str],
                           active: Optional[bool], p: Optional[str]):
        from sqlalchemy import or_

        query = select(User).order_by(desc(User.created_at))
        if skill:
            query = query.join(users_skills.UserSkill).join(Skill).filter(
                Skill.name == skill.capitalize()
            )
        if stack:
            query = query.filter(User.stack.has(name=stack.capitalize()))
        if active is not None:
            if active:  # active=True means Directory
                # Only show ACCEPTED + is_active users
                query = query.filter(User.is_active.is_(True), User.status == "ACCEPTED")
            else:  # active=False means Applicants
                # Show: (is_active=false any status) OR (is_active=true but status != ACCEPTED)
                query = query.filter(
                    or_(
                        User.is_active.is_(False),
                        User.is_active.is_(True) & (User.status != "ACCEPTED")
                    )
                )
        if p:
            p_escaped = p.replace("%", r"\%").replace("_", r"\_")
            query = query.filter(
                User.username.ilike(f"%{p_escaped}%", escape="\\")
                | User.first_name.ilike(f"%{p_escaped}%", escape="\\")
                | User.last_name.ilike(f"%{p_escaped}%", escape="\\")
            )
        return query


# Backwards-compatibility shim — remove in Phase 4 once all callers use UserRepository directly
def create_new_user(user: UserSignUp, db: Session) -> User:
    return UserRepository(db).create(user)
