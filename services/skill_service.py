from typing import Optional

from fastapi import HTTPException, status
from rapidfuzz import fuzz, process

from db.models.skills import Skill
from db.models.users import User
from db.repository.skills import SkillRepository


class SkillService:
    def __init__(self, skill_repo: SkillRepository):
        self.skill_repo = skill_repo

    def get_user_skills(self, user_id: int) -> list[Skill]:
        return self.skill_repo.get_all_for_user(user_id)

    def add_skills(self, current_user: User, skill_ids: list[int]) -> list[Skill]:
        db_skills = self.skill_repo.get_by_ids(skill_ids)
        if not db_skills:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No skills found with the given ids"
            )
        existing = self.skill_repo.get_user_skill_entries(current_user.id, skill_ids)
        if existing:
            existing_ids = [e.skill_id for e in existing]
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User already has skills with IDs: {existing_ids}"
            )
        return self.skill_repo.add_skills_to_user(current_user.id, db_skills, current_user)

    def delete_skill(self, skill_id: int) -> None:
        entry = self.skill_repo.get_user_skill_entry(skill_id)
        if not entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No skill with this id: {skill_id} found"
            )
        self.skill_repo.delete_user_skill(skill_id)

    def get_all_query(self):
        return self.skill_repo.get_all_paginated_query()

    def populate_skills(self) -> dict:
        from db.database import create_roles
        from utils.endpoints_status import create_signup_endpoint
        from utils.tools import tools as skills_data, get_skills_image

        create_roles()
        create_signup_endpoint(status=True)

        try:
            last_skill = None
            for skill_name in skills_data:
                last_skill = self.skill_repo.upsert(skill_name, get_skills_image(skill_name))
            self.skill_repo.db.commit()
            if last_skill:
                self.skill_repo.db.refresh(last_skill)
        except Exception as e:
            self.skill_repo.db.rollback()
            raise HTTPException(status_code=500, detail=f"Error populating skills: {e}")
        return {"message": "Skills table populated successfully!"}

    def search_skills(self, name: str) -> list[dict]:
        skills = self.skill_repo.get_all_flat()
        threshold = 78
        return [
            {"skill_id": skill.id, "skill_name": skill.name}
            for skill in skills
            if fuzz.partial_ratio(name.lower(), skill.name.lower()) >= threshold
        ]
