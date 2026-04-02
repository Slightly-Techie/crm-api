from typing import List, Optional

from fastapi import HTTPException, status

from api.api_models.projects import CreateProject, UpdateProject
from db.models.projects import Project
from db.models.users import User
from db.models.users_projects import UserProject
from db.repository.projects import ProjectRepository
from db.repository.skills import SkillRepository
from db.repository.stacks import StackRepository
from db.repository.users import UserRepository
from utils.enums import ProjectTeam


class ProjectService:
    def __init__(self, project_repo: ProjectRepository, user_repo: UserRepository,
                 stack_repo: StackRepository, skill_repo: SkillRepository):
        self.project_repo = project_repo
        self.user_repo = user_repo
        self.stack_repo = stack_repo
        self.skill_repo = skill_repo

    def _enrich_project_members_with_team(self, project: Project) -> Project:
        """Add team role data from users_projects join table to project members."""
        for member in project.members:
            user_project = self.project_repo.db.query(UserProject).filter(
                UserProject.user_id == member.id,
                UserProject.project_id == project.id
            ).first()
            if user_project:
                # Dynamically set the team attribute for Pydantic serialization
                object.__setattr__(member, 'team', user_project.team)
        return project

    def create_project(self, project_data: CreateProject) -> Project:
        manager = self.user_repo.get_by_id(project_data.manager_id)
        if not manager:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Manager not found")

        data = project_data.model_dump(exclude=["members", "stacks", "project_tools"])
        new_project = Project(**data)

        # Note: Members are NOT added here. They are added separately via the /add/{userId} endpoint
        # with their team roles specified. This ensures the users_projects join table has the team field set.

        if project_data.stacks:
            seen = []
            for stack_id in project_data.stacks:
                if stack_id in seen:
                    raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                                        detail=f"Duplicate stack id: {stack_id}")
                stack = self.stack_repo.get_by_id(stack_id)
                if not stack:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                        detail=f"Stack {stack_id} not found")
                new_project.stacks.append(stack)
                seen.append(stack_id)

        if project_data.project_tools:
            seen = []
            for skill_id in project_data.project_tools:
                if skill_id in seen:
                    raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                                        detail=f"Duplicate skill id: {skill_id}")
                skill = self.skill_repo.get_by_id(skill_id)
                if not skill:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                        detail=f"Skill {skill_id} not found")
                new_project.project_tools.append(skill)
                seen.append(skill_id)

        saved = self.project_repo.save(new_project)
        return self._enrich_project_members_with_team(saved)

    def update_project(self, project_id: int, update_data: UpdateProject) -> Project:
        project = self.project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        if update_data.manager_id is not None:
            if update_data.manager_id != project.manager_id:
                if not self.user_repo.get_by_id(update_data.manager_id):
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Manager not found")
        updated = self.project_repo.update(
            project, update_data.model_dump(exclude=["members", "stacks", "project_tools"], exclude_none=True)
        )
        return self._enrich_project_members_with_team(updated)

    def delete_project(self, project_id: int) -> None:
        project = self.project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        self.project_repo.delete_with_memberships(project_id)

    def get_project(self, project_id: int) -> Project:
        project = self.project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        return self._enrich_project_members_with_team(project)

    def get_all_query(self):
        return self.project_repo.get_all_paginated_query()

    def add_member(self, project_id: int, user_id: int, team: ProjectTeam) -> dict:
        if not self.project_repo.get_by_id(project_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        if not self.user_repo.get_by_id(user_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        if self.project_repo.get_member_entry(user_id, project_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="User is already a member of the project")
        self.project_repo.add_member(user_id, project_id, team)
        return {"message": "User added to project with team specified"}

    def remove_member(self, project_id: int, user_id: int) -> None:
        if not self.project_repo.get_by_id(project_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        if not self.user_repo.get_by_id(user_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        entry = self.project_repo.get_member_entry(user_id, project_id)
        if not entry:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="User is not associated with the project")
        self.project_repo.remove_member(entry)

    def get_project_members(self, project_id: int, team: Optional[ProjectTeam]) -> List[User]:
        if not self.project_repo.get_by_id(project_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        members = self.project_repo.get_members(project_id, team)
        # Enrich members with team data
        for member in members:
            user_project = self.project_repo.db.query(UserProject).filter(
                UserProject.user_id == member.id,
                UserProject.project_id == project_id
            ).first()
            if user_project:
                object.__setattr__(member, 'team', user_project.team)
        return members
