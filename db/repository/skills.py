from typing import Any, Optional

from sqlalchemy import desc, select
from sqlalchemy.orm import joinedload

from db.models.skills import Skill
from db.models.users import User
from db.models.users_skills import UserSkill
from db.repository.base import BaseRepository


class SkillRepository(BaseRepository):
    model = Skill

    def get_all_for_user(self, user_id: int) -> list[Skill]:
        user = self.db.query(User).filter(User.id == user_id).options(
            joinedload(User.skills)
        ).first()
        return user.skills if user else []

    def get_by_ids(self, skill_ids: list[int]) -> list[Skill]:
        return self.db.query(Skill).filter(Skill.id.in_(skill_ids)).all()

    def get_user_skill_entries(self, user_id: int, skill_ids: list[int]) -> list[UserSkill]:
        return self.db.query(UserSkill).filter(
            UserSkill.skill_id.in_(skill_ids),
            UserSkill.user_id == user_id
        ).all()

    def add_skills_to_user(self, user_id: int, skills: list[Skill], current_user: User) -> list[Skill]:
        user_skills = [UserSkill(user_id=user_id, skill_id=skill.id) for skill in skills]
        self.db.add_all(user_skills)
        self.db.commit()
        self.db.refresh(current_user)
        return current_user.skills

    def delete_user_skill(self, skill_id: int) -> None:
        query = self.db.query(UserSkill).filter(UserSkill.skill_id == skill_id)
        query.delete(synchronize_session=False)
        self.db.commit()

    def get_user_skill_entry(self, skill_id: int) -> Optional[UserSkill]:
        return self.db.query(UserSkill).filter(UserSkill.skill_id == skill_id).first()

    def get_all_flat(self) -> list[Skill]:
        return self.db.query(Skill).all()

    def get_all_paginated_query(self) -> Any:
        return select(Skill).order_by(desc(Skill.created_at))

    def get_by_name(self, name: str) -> Optional[Skill]:
        return self.db.query(Skill).filter(Skill.name == name).first()

    def upsert(self, name: str, image_url: Optional[str]) -> Skill:
        skill = self.get_by_name(name)
        if skill:
            if not skill.image_url and image_url:
                skill.image_url = image_url
        else:
            skill = Skill(name=name, image_url=image_url)
        self.db.add(skill)
        return skill
