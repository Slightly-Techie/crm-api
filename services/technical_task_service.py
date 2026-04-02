from fastapi import HTTPException, status

from db.models.technical_task import TechnicalTask, TechnicalTaskSubmission
from db.models.users import User
from db.repository.technical_tasks import TechnicalTaskRepository, TechnicalTaskSubmissionRepository
from utils.utils import get_key_by_value


class TechnicalTaskService:
    def __init__(self, task_repo: TechnicalTaskRepository,
                 submission_repo: TechnicalTaskSubmissionRepository):
        self.task_repo = task_repo
        self.submission_repo = submission_repo

    # --- Tasks ---

    def create_task(self, data: dict) -> TechnicalTask:
        try:
            return self.task_repo.create(data)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    def get_all_tasks(self) -> list[TechnicalTask]:
        tasks = self.task_repo.get_all()
        if not tasks:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No Technical Tasks exist at the moment"
            )
        return tasks

    def get_task(self, task_id: int) -> TechnicalTask:
        task = self.task_repo.get_by_id(task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Technical Task with id {task_id} is not found"
            )
        return task

    def update_task(self, task_id: int, payload: dict) -> TechnicalTask:
        self.get_task(task_id)  # raises 404 if not found
        try:
            return self.task_repo.update(task_id, payload)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    def delete_task(self, task_id: int) -> None:
        self.get_task(task_id)  # raises 404 if not found
        try:
            self.task_repo.delete_by_id(task_id)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    # --- Submissions ---

    def create_submission(self, current_user: User, data: dict) -> TechnicalTaskSubmission:
        # Check if user has required profile information
        if not current_user.stack_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Please complete your profile by selecting a tech stack before submitting."
            )

        if current_user.years_of_experience is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Please complete your profile by adding years of experience before submitting."
            )

        try:
            user_exp = get_key_by_value(current_user.years_of_experience)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        task = self.task_repo.get_by_stack_and_level(current_user.stack_id, user_exp)

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    f"No technical task found for your stack and experience level "
                    f"(stack_id={current_user.stack_id}, experience_level={user_exp}). "
                    f"Please contact admin at info@slightlytechie.com."
                )
            )

        # Check if user already submitted
        existing_submission = self.submission_repo.get_existing_for_user(current_user.id)
        if existing_submission:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You have already submitted a task. Multiple submissions are not allowed. Contact admin if you need to update your submission."
            )

        try:
            return self.submission_repo.create(task.id, current_user.id, data)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to submit task: {str(e)}"
            )

    def get_all_submissions(self) -> list[TechnicalTaskSubmission]:
        submissions = self.submission_repo.get_all()
        if not submissions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No Submissions exist at the moment"
            )
        return submissions

    def get_submission(self, submission_id: int) -> TechnicalTaskSubmission:
        submission = self.submission_repo.get_by_id(submission_id)
        if not submission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task Submission with id {submission_id} is not found"
            )
        return submission

    def update_submission(self, submission_id: int, payload: dict) -> TechnicalTaskSubmission:
        self.get_submission(submission_id)  # raises 404 if not found
        try:
            return self.submission_repo.update(submission_id, payload)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    def get_submission_by_user(self, user_id: int) -> TechnicalTaskSubmission:
        submission = self.submission_repo.get_by_user_id(user_id)
        if not submission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task Submission not found for user with id {user_id}"
            )
        return submission
