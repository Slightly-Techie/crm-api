from datetime import datetime
from typing import Optional

from sqlalchemy import desc, select

from db.models.projects import Project
from db.models.users import User
from db.models.users_projects import UserProject
from db.repository.base import BaseRepository


class ProjectRepository(BaseRepository):
    model = Project

    def get_all_paginated_query(self):
        return select(Project).order_by(desc(Project.created_at))

    def create(self, data: dict) -> Project:
        project = Project(**data)
        return self.save(project)

    def update(self, project: Project, update_data: dict) -> Project:
        for field, value in update_data.items():
            if value is not None:
                setattr(project, field, value)
        project.updated_at = datetime.now()
        self.db.commit()
        self.db.refresh(project)
        return project

    def delete_with_memberships(self, project_id: int) -> None:
        self.db.query(UserProject).filter(UserProject.project_id == project_id).delete()
        self.db.query(Project).filter(Project.id == project_id).delete()
        self.db.commit()

    def get_member_entry(self, user_id: int, project_id: int) -> Optional[UserProject]:
        return self.db.query(UserProject).filter(
            UserProject.user_id == user_id,
            UserProject.project_id == project_id
        ).first()

    def add_member(self, user_id: int, project_id: int, team: str) -> None:
        entry = UserProject(user_id=user_id, project_id=project_id, team=team)
        self.db.add(entry)
        self.db.commit()

    def remove_member(self, entry: UserProject) -> None:
        self.db.delete(entry)
        self.db.commit()

    def get_members(self, project_id: int, team: Optional[str] = None) -> list[User]:
        query = self.db.query(UserProject).filter(UserProject.project_id == project_id)
        if team:
            query = query.filter(UserProject.team == team)
        user_ids = [row.user_id for row in query.all()]
        return self.db.query(User).filter(User.id.in_(user_ids)).all()
