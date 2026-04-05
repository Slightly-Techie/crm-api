"""Routes for technical task and submission"""
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from api.api_models.technical_task import (
    TechnicalTaskBase, TechnicalTaskResponse,
    TechnicalTaskSubmissionBase, TechnicalTaskSubmissionResponse
)
from db.database import get_db
from db.repository.technical_tasks import TechnicalTaskRepository, TechnicalTaskSubmissionRepository
from services.technical_task_service import TechnicalTaskService
from utils.permissions import is_admin, user_accepted

tech_task_router = APIRouter(tags=["Applicant Task"], prefix="/applicant/task")
sub_tech_task_router = APIRouter(tags=["Applicant Task Submission"], prefix="/applicant/submission")


def _service(db: Session) -> TechnicalTaskService:
    return TechnicalTaskService(TechnicalTaskRepository(db), TechnicalTaskSubmissionRepository(db))


@tech_task_router.post("/", status_code=status.HTTP_201_CREATED, response_model=TechnicalTaskResponse)
def create_task(tech_task: TechnicalTaskBase, current_user=Depends(is_admin),
                db: Session = Depends(get_db), user_status=Depends(user_accepted)):
    return _service(db).create_task(dict(tech_task))


@tech_task_router.get("/", status_code=status.HTTP_200_OK, response_model=list[TechnicalTaskResponse])
def get_tasks(current_user=Depends(user_accepted), db: Session = Depends(get_db)):
    return _service(db).get_all_tasks()


@tech_task_router.patch("/{task_id}", status_code=status.HTTP_200_OK,
                        response_model=TechnicalTaskResponse)
def update_task(task_id: int, payload: TechnicalTaskBase, current_user=Depends(is_admin),
                db: Session = Depends(get_db), user_status=Depends(user_accepted)):
    return _service(db).update_task(task_id, payload.model_dump(exclude_unset=True))


@tech_task_router.get("/{task_id}", status_code=status.HTTP_200_OK,
                      response_model=TechnicalTaskResponse)
def get_task(task_id: int, current_user=Depends(user_accepted), db: Session = Depends(get_db)):
    return _service(db).get_task(task_id)


@tech_task_router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, current_user=Depends(is_admin), db: Session = Depends(get_db),
                user_status=Depends(user_accepted)):
    _service(db).delete_task(task_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@sub_tech_task_router.post("/", status_code=status.HTTP_201_CREATED,
                           response_model=TechnicalTaskSubmissionResponse)
def create_task_submission(tech_task: TechnicalTaskSubmissionBase,
                           current_user=Depends(user_accepted), db: Session = Depends(get_db)):
    return _service(db).create_submission(current_user, dict(tech_task))


@sub_tech_task_router.get("/", status_code=status.HTTP_200_OK,
                          response_model=list[TechnicalTaskSubmissionResponse])
def get_task_submissions(current_user=Depends(user_accepted), db: Session = Depends(get_db)):
    return _service(db).get_all_submissions()


@sub_tech_task_router.patch("/{submission_id}", status_code=status.HTTP_200_OK,
                            response_model=TechnicalTaskSubmissionResponse)
def update_submission(submission_id: int, payload: TechnicalTaskSubmissionBase,
                      current_user=Depends(user_accepted), db: Session = Depends(get_db)):
    return _service(db).update_submission(submission_id, payload.model_dump(exclude_unset=True))


@sub_tech_task_router.get("/{submission_id}", status_code=status.HTTP_200_OK,
                          response_model=TechnicalTaskSubmissionResponse)
def get_submission(submission_id: int, current_user=Depends(user_accepted),
                   db: Session = Depends(get_db)):
    return _service(db).get_submission(submission_id)


@sub_tech_task_router.get("/{user_id}/users", status_code=status.HTTP_200_OK,
                          response_model=TechnicalTaskSubmissionResponse)
def get_submission_by_user(user_id: int, current_user=Depends(user_accepted),
                           db: Session = Depends(get_db)):
    return _service(db).get_submission_by_user(user_id)
