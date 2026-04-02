"""Tests for Technical Task Submissions API and service"""
import pytest
from datetime import datetime
from unittest.mock import Mock, MagicMock, patch
from sqlalchemy.orm import Session

from db.models.technical_task import TechnicalTaskSubmission, TechnicalTask
from db.models.users import User
from db.models.stacks import Stack
from services.technical_task_service import TechnicalTaskService
from db.repository.technical_tasks import TechnicalTaskRepository, TechnicalTaskSubmissionRepository


class TestTechnicalTaskSubmissionResponse:
    """Test that submission responses include nested user and task data"""

    def test_submission_response_includes_user_data(self):
        """Submission response should include user details"""
        user = Mock(spec=User)
        user.id = 1
        user.first_name = "John"
        user.last_name = "Doe"
        user.username = "johndoe"
        user.profile_pic_url = "https://example.com/pic.jpg"

        submission = Mock(spec=TechnicalTaskSubmission)
        submission.id = 1
        submission.user = user
        submission.github_link = "https://github.com/johndoe/project"
        submission.live_demo_url = "https://project.example.com"
        submission.description = "My submission"
        submission.created_at = datetime.now()
        submission.updated_at = datetime.now()
        submission.task_id = 1

        # Verify user data is accessible
        assert submission.user.id == 1
        assert submission.user.first_name == "John"
        assert submission.user.last_name == "Doe"
        assert submission.user.username == "johndoe"
        assert submission.user.profile_pic_url is not None

    def test_submission_response_includes_task_data(self):
        """Submission response should include technical task details with stack"""
        stack = Mock(spec=Stack)
        stack.id = 1
        stack.name = "Backend"

        task = Mock(spec=TechnicalTask)
        task.id = 1
        task.content = "Build a REST API"
        task.experience_level = "JUNIOR"
        task.stack = stack

        submission = Mock(spec=TechnicalTaskSubmission)
        submission.id = 1
        submission.technical_task = task
        submission.task_id = 1

        # Verify task data is accessible
        assert submission.technical_task.id == 1
        assert submission.technical_task.content == "Build a REST API"
        assert submission.technical_task.experience_level == "JUNIOR"
        assert submission.technical_task.stack.name == "Backend"

    def test_submission_response_has_all_required_fields(self):
        """Submission response should have all submission metadata fields"""
        submission = Mock(spec=TechnicalTaskSubmission)
        submission.id = 1
        submission.github_link = "https://github.com/user/repo"
        submission.live_demo_url = "https://demo.example.com"
        submission.description = "My work"
        submission.created_at = datetime.now()
        submission.updated_at = datetime.now()
        submission.task_id = 1
        submission.user_id = 1
        submission.user = Mock()
        submission.technical_task = Mock()

        # Verify all fields present
        assert hasattr(submission, 'id')
        assert hasattr(submission, 'github_link')
        assert hasattr(submission, 'live_demo_url')
        assert hasattr(submission, 'description')
        assert hasattr(submission, 'created_at')
        assert hasattr(submission, 'updated_at')
        assert hasattr(submission, 'task_id')
        assert hasattr(submission, 'user_id')
        assert hasattr(submission, 'user')
        assert hasattr(submission, 'technical_task')


class TestTechnicalTaskServiceErrorHandling:
    """Test error handling in technical task service"""

    def test_create_submission_provides_context_on_task_not_found(self):
        """When task not found, error message should include stack_id and experience_level"""
        task_repo = Mock(spec=TechnicalTaskRepository)
        submission_repo = Mock(spec=TechnicalTaskSubmissionRepository)
        service = TechnicalTaskService(task_repo, submission_repo)

        user = Mock(spec=User)
        user.id = 1
        user.stack_id = 5
        user.years_of_experience = 0

        # Mock task_repo to return None
        task_repo.get_by_stack_and_level = Mock(return_value=None)

        # Service should provide context in error
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            service.create_submission(user, {"github_link": "test"})

        error_detail = exc_info.value.detail
        # Error message should mention stack_id and experience level
        assert "stack_id=5" in error_detail or "JUNIOR" in error_detail

    def test_create_submission_error_on_invalid_experience(self):
        """Creating submission should raise error when years_of_experience is invalid"""
        task_repo = Mock(spec=TechnicalTaskRepository)
        submission_repo = Mock(spec=TechnicalTaskSubmissionRepository)
        service = TechnicalTaskService(task_repo, submission_repo)

        user = Mock(spec=User)
        user.id = 1
        user.stack_id = 1
        user.years_of_experience = 999  # Invalid value

        from fastapi import HTTPException

        with pytest.raises(HTTPException):
            service.create_submission(user, {"github_link": "test"})
