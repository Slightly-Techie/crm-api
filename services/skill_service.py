from fastapi import HTTPException, status
from rapidfuzz import fuzz

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

    def get_all_query(self) -> list[Skill]:
        return self.skill_repo.get_all_paginated_query()

    def populate_skills(self) -> dict:
        from db.database import create_roles
        from utils.endpoints_status import create_signup_endpoint
        from utils.tools import tools as skills_data, get_skills_image
        import logging

        logger = logging.getLogger(__name__)

        # Try to create roles - catch expected "already exists" exceptions
        try:
            create_roles()
        except Exception as e:
            # Expected when roles already exist; log unexpected errors for diagnostics
            if "already" not in str(e).lower():
                logger.warning(f"Unexpected error creating roles: {e}")

        # Try to create signup endpoint - catch expected "already exists" exceptions
        try:
            create_signup_endpoint(status=True)
        except Exception as e:
            # Expected when endpoint already exists; log unexpected errors for diagnostics
            if "already" not in str(e).lower():
                logger.warning(f"Unexpected error creating signup endpoint: {e}")

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
            {
                "skill_id": skill.id,
                "skill_name": skill.name,

                "image_url": skill.image_url or ""
            }
            for skill in skills
            if fuzz.partial_ratio(name.lower(), skill.name.lower()) >= threshold
        ]

    def create_pool_skill(self, name: str, image_url=None):
        existing = self.skill_repo.get_by_name(name)
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Skill '{name}' already exists"
            )
        return self.skill_repo.create(name, image_url)

    def delete_pool_skill(self, skill_id: int) -> None:
        skill = self.skill_repo.get_by_id(skill_id)
        if not skill:
            raise HTTPException(
                status_code=404,
                detail=f"Skill with id {skill_id} not found"
            )
        self.skill_repo.delete_from_pool(skill_id)
