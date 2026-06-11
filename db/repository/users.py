from typing import Optional

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from api.api_models.user import UserSignUp
from db.models.users import User
from db.models.skills import Skill
from db.models.tags import Tag
from db.models import users_skills
from db.repository.base import BaseRepository

# Upwork-style experience bands: level name -> (min_years, max_years|None)
EXPERIENCE_LEVELS = {
    "entry": (0, 2),
    "intermediate": (3, 5),
    "expert": (6, None),
}


def experience_level_filter(levels: list[str]):
    """OR together the year-ranges for the selected experience levels."""
    from sqlalchemy import or_, and_

    conditions = []
    for level in levels:
        bounds = EXPERIENCE_LEVELS.get(level.lower())
        if not bounds:
            continue
        low, high = bounds
        cond = User.years_of_experience >= low
        if high is not None:
            cond = and_(cond, User.years_of_experience <= high)
        conditions.append(cond)
    return or_(*conditions) if conditions else None


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
                           active: Optional[bool], p: Optional[str],
                           status: Optional[str] = None,
                           tags: Optional[list[str]] = None,
                           min_experience: Optional[int] = None,
                           max_experience: Optional[int] = None,
                           open_to_projects: Optional[bool] = None,
                           skills: Optional[list[str]] = None,
                           experience_levels: Optional[list[str]] = None,
                           created_after=None):
        from sqlalchemy import or_, func

        query = select(User).order_by(desc(User.created_at))
        if created_after is not None:
            query = query.filter(User.created_at >= created_after)
        if skill:
            query = query.join(users_skills.UserSkill).join(Skill).filter(
                Skill.name == skill.capitalize()
            )
        if skills:
            # Match ANY of the selected skills; .any() avoids join-row duplication
            skill_names = [s.capitalize() for s in skills if s]
            if skill_names:
                query = query.filter(User.skills.any(Skill.name.in_(skill_names)))
        if stack:
            query = query.filter(User.stack.has(name=stack.capitalize()))
        if tags:
            # Match ANY of the selected tags (case-insensitive); tags are stored lower-case
            tag_names = [t.lower() for t in tags if t]
            if tag_names:
                query = query.filter(User.tags.any(Tag.name.in_(tag_names)))
        if min_experience is not None:
            query = query.filter(User.years_of_experience >= min_experience)
        if max_experience is not None:
            query = query.filter(User.years_of_experience <= max_experience)
        if experience_levels:
            level_filter = experience_level_filter(experience_levels)
            if level_filter is not None:
                query = query.filter(level_filter)
        if open_to_projects is not None:
            query = query.filter(User.open_to_projects.is_(open_to_projects))
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
        if status:
            query = query.filter(User.status == status)
        if p:
            p_escaped = p.replace("%", r"\%").replace("_", r"\_")
            full_name = func.concat(User.first_name, " ", User.last_name)
            query = query.filter(
                User.username.ilike(f"%{p_escaped}%", escape="\\")
                | User.first_name.ilike(f"%{p_escaped}%", escape="\\")
                | User.last_name.ilike(f"%{p_escaped}%", escape="\\")
                | User.email.ilike(f"%{p_escaped}%", escape="\\")
                | full_name.ilike(f"%{p_escaped}%", escape="\\")
            )
        return query


# Backwards-compatibility shim — remove in Phase 4 once all callers use UserRepository directly
def create_new_user(user: UserSignUp, db: Session) -> User:
    return UserRepository(db).create(user)
