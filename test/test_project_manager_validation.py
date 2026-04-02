"""Tests for Project service manager validation"""
import pytest
from unittest.mock import Mock
from fastapi import HTTPException
from api.api_models.projects import UpdateProject
from services.project_service import ProjectService
from db.repository.projects import ProjectRepository
from db.repository.users import UserRepository
from db.repository.skills import SkillRepository
from db.repository.stacks import StackRepository


class TestProjectManagerValidation:
    """Test project manager assignment and validation"""

    def test_update_manager_validates_manager_exists(self):
        """Updating project manager should validate manager exists"""
        project_repo = Mock(spec=ProjectRepository)
        user_repo = Mock(spec=UserRepository)
        skill_repo = Mock(spec=SkillRepository)
        stack_repo = Mock(spec=StackRepository)

        service = ProjectService(project_repo, user_repo, stack_repo, skill_repo)

        # Mock existing project
        mock_project = Mock()
        mock_project.id = 1
        mock_project.manager_id = 1
        project_repo.get_by_id = Mock(return_value=mock_project)

        # Mock user_repo to return None (manager doesn't exist)
        user_repo.get_by_id = Mock(return_value=None)

        update_data = UpdateProject(manager_id=999, name=None, description=None, project_type=None, project_priority=None, project_tools=None)

        with pytest.raises(HTTPException) as exc_info:
            service.update_project(1, update_data)

        assert exc_info.value.status_code == 404
        assert "Manager not found" in exc_info.value.detail

    def test_update_manager_skips_validation_when_same(self):
        """Updating manager to same value should skip existence check"""
        project_repo = Mock(spec=ProjectRepository)
        user_repo = Mock(spec=UserRepository)
        skill_repo = Mock(spec=SkillRepository)
        stack_repo = Mock(spec=StackRepository)

        service = ProjectService(project_repo, user_repo, stack_repo, skill_repo)

        # Mock existing project with manager_id = 5
        mock_project = Mock()
        mock_project.id = 1
        mock_project.manager_id = 5
        mock_project.members = []  # Add empty members list for _enrich_project_members_with_team
        project_repo.get_by_id = Mock(return_value=mock_project)

        # Mock update to return project
        project_repo.update = Mock(return_value=mock_project)

        update_data = UpdateProject(manager_id=5, name=None, description=None, project_type=None, project_priority=None, project_tools=None)

        # Should not raise error - validation skipped when same manager
        service.update_project(1, update_data)

        # user_repo.get_by_id should NOT be called since manager is same
        user_repo.get_by_id.assert_not_called()

    def test_update_manager_success_with_valid_manager(self):
        """Updating project manager should succeed with valid manager"""
        project_repo = Mock(spec=ProjectRepository)
        user_repo = Mock(spec=UserRepository)
        skill_repo = Mock(spec=SkillRepository)
        stack_repo = Mock(spec=StackRepository)

        service = ProjectService(project_repo, user_repo, stack_repo, skill_repo)

        # Mock existing project
        mock_project = Mock()
        mock_project.id = 1
        mock_project.manager_id = 1
        mock_project.members = []
        project_repo.get_by_id = Mock(return_value=mock_project)

        # Mock valid manager exists
        mock_manager = Mock()
        mock_manager.id = 5
        user_repo.get_by_id = Mock(return_value=mock_manager)

        # Mock update to return updated project
        updated_project = Mock()
        updated_project.id = 1
        updated_project.manager_id = 5
        updated_project.members = []  # Add empty members list for _enrich_project_members_with_team
        project_repo.update = Mock(return_value=updated_project)

        update_data = UpdateProject(manager_id=5, name=None, description=None, project_type=None, project_priority=None, project_tools=None)

        result = service.update_project(1, update_data)

        # Should succeed
        assert result is not None
        user_repo.get_by_id.assert_called_with(5)

    def test_update_project_not_found(self):
        """Updating non-existent project should raise 404"""
        project_repo = Mock(spec=ProjectRepository)
        user_repo = Mock(spec=UserRepository)
        skill_repo = Mock(spec=SkillRepository)
        stack_repo = Mock(spec=StackRepository)

        service = ProjectService(project_repo, user_repo, stack_repo, skill_repo)

        # Mock project doesn't exist
        project_repo.get_by_id = Mock(return_value=None)

        update_data = UpdateProject(manager_id=1, name=None, description=None, project_type=None, project_priority=None, project_tools=None)

        with pytest.raises(HTTPException) as exc_info:
            service.update_project(999, update_data)

        assert exc_info.value.status_code == 404
        assert "Project not found" in exc_info.value.detail

    def test_update_exclude_none_values(self):
        """Update should only send non-None fields to repository"""
        project_repo = Mock(spec=ProjectRepository)
        user_repo = Mock(spec=UserRepository)
        skill_repo = Mock(spec=SkillRepository)
        stack_repo = Mock(spec=StackRepository)

        service = ProjectService(project_repo, user_repo, stack_repo, skill_repo)

        # Mock existing project
        mock_project = Mock()
        mock_project.id = 1
        mock_project.manager_id = 1
        mock_project.members = []  # Add empty members list for _enrich_project_members_with_team
        project_repo.get_by_id = Mock(return_value=mock_project)
        project_repo.update = Mock(return_value=mock_project)

        # Update with only name (others None)
        update_data = UpdateProject(
            name="New Name",
            description=None,
            project_type=None,
            project_priority=None,
            manager_id=None,
            project_tools=None
        )

        service.update_project(1, update_data)

        # Verify project_repo.update was called
        project_repo.update.assert_called_once()

        # Get the actual call arguments
        call_args = project_repo.update.call_args
        update_dict = call_args[0][1]  # Second argument is the update dict

        # Verify only non-None fields are in update dict
        assert "name" in update_dict
        assert update_dict["name"] == "New Name"
        # None fields should not be in the dict due to exclude_none=True
        if "description" in update_dict:
            assert update_dict["description"] is not None
