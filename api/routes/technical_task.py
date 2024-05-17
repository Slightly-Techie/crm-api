"""
Routes foe the technical task and submission
"""
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
# from db.models.users import User
from db.models.technical_task import TechnicalTask, TechnicalTaskSubmission
from api.api_models.technical_task import (
    TechnicalTaskBase, TechnicalTaskResponse,
    TechnicalTaskSubmissionBase, TechnicalTaskSubmissionResponse
)
from utils.permissions import is_admin, user_accepted, get_current_user
from db.database import get_db
from utils.utils import get_key_by_value


tech_task_router = APIRouter(tags=["Applicant Task"], prefix="/applicant/task")
sub_tech_task_router = APIRouter(tags=["Applicant Task"], prefix="/applicant/submission")


@tech_task_router.post("/", status_code=status.HTTP_201_CREATED, response_model=TechnicalTaskResponse)
def create_task(
    tech_task: TechnicalTaskBase, current_user=Depends(is_admin),
    db: Session = Depends(get_db), user_status=Depends(user_accepted)
):
    """Create the technical task"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    new_tech_task = TechnicalTask(**dict(tech_task))
    try:
        db.add(new_tech_task)
        db.commit()
        db.refresh(new_tech_task)
        return new_tech_task
    except Exception as task_err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=task_err.__str__()
        )


@tech_task_router.get("/", status_code=status.HTTP_200_OK, response_model=list[TechnicalTaskResponse])
def get_tasks(
    current_user=Depends(get_current_user), db: Session = Depends(get_db), user_status=Depends(user_accepted)
):
    """Get all the technical tasks"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    db_query = db.query(TechnicalTask).all()
    if not db_query:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="No Technical Tasks exist at the moment")
    return db_query


@tech_task_router.patch("/{task_id}", status_code=status.HTTP_200_OK, response_model=TechnicalTaskResponse)
def update_task(
    task_id: int, payload: TechnicalTaskBase, current_user=Depends(is_admin),
    db: Session = Depends(get_db), user_status=Depends(user_accepted)
):
    """Get a technical task"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    tech_task = db.query(TechnicalTask).filter(TechnicalTask.id == task_id)
    old_task = tech_task.first()

    if not old_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Technical Task with id {task_id} is not found"
            )
    try:
        tech_task.update(payload.model_dump(exclude_unset=True))
        db.commit()
        db.refresh(old_task)
    except Exception as tech_update_err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=tech_update_err.__str__()
        )
    return old_task


@tech_task_router.get("/{task_id}", status_code=status.HTTP_200_OK, response_model=TechnicalTaskResponse)
def get_task(
    task_id: int, current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a technical task"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    tech_task = db.query(TechnicalTask).filter(TechnicalTask.id == task_id).first()

    if not tech_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Technical Task with id {task_id} is not found"
            )
    return tech_task


@tech_task_router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int, current_user=Depends(is_admin),
    db: Session = Depends(get_db), user_status=Depends(user_accepted)
):
    """Delete a technical task by ID"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    tech_task = db.query(TechnicalTask).filter(TechnicalTask.id == task_id)
    old_task = tech_task.first()

    if not old_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Technical Task with id {task_id} is not found"
            )
    try:
        tech_task.delete()
        db.commit()
    except Exception as tech_upadte_err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=dict(tech_upadte_err.__str__())
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@sub_tech_task_router.post(
        "/", status_code=status.HTTP_201_CREATED, response_model=TechnicalTaskSubmissionResponse)
def create_task_submission(
    tech_task: TechnicalTaskSubmissionBase, current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit the technical task"""
    user_exp = get_key_by_value(current_user.years_of_experience)
    print(current_user.stack_id)
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    user_task = db.query(TechnicalTask).filter(
        TechnicalTask.stack_id == current_user.stack_id,
        TechnicalTask.experience_level == user_exp
        ).first()
    if not user_task:
        raise HTTPException(
           status_code=404, detail="Cannot find a task for this submission"
        )
    new_tech_task = TechnicalTaskSubmission(
        task_id=user_task.id,
        user_id=current_user.id, **dict(tech_task)
        )
    try:
        db.add(new_tech_task)
        db.commit()
        db.refresh(new_tech_task)
        return new_tech_task
    except Exception as task_err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=task_err.__str__()
        )


@sub_tech_task_router.get(
        "/", status_code=status.HTTP_200_OK, response_model=list[TechnicalTaskSubmissionResponse])
def get_task_submissions(
    current_user=Depends(get_current_user), db: Session = Depends(get_db), user_status=Depends(user_accepted)
):
    """Get all the tasks Submissions"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    db_query = db.query(TechnicalTaskSubmission).all()
    if not db_query:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="No Submissions exist at the moment")
    return db_query


@sub_tech_task_router.patch(
        "/{submission_id}", status_code=status.HTTP_200_OK, response_model=TechnicalTaskSubmissionResponse)
def update_submission(
    submission_id: int, payload: TechnicalTaskSubmissionBase, current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a Submission of a task"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    tech_task = db.query(TechnicalTaskSubmission).filter(TechnicalTaskSubmission.id == submission_id)
    old_task = tech_task.first()

    if not old_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task Submission with id {submission_id} is not found"
            )
    try:
        tech_task.update(payload.model_dump(exclude_unset=True))
        db.commit()
        db.refresh(old_task)
    except Exception as tech_update_err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=tech_update_err.__str__()
        )
    return old_task


@sub_tech_task_router.get(
        "/{submission_id}", status_code=status.HTTP_200_OK, response_model=TechnicalTaskSubmissionResponse)
def get_submission(
    submission_id: int, current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a task Submission"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    tech_task = db.query(TechnicalTaskSubmission).filter(TechnicalTaskSubmission.id == submission_id).first()

    if not tech_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task Submission with id {submission_id} is not found"
            )
    return tech_task


@sub_tech_task_router.get(
        "/{user_id}/users", status_code=status.HTTP_200_OK, response_model=TechnicalTaskSubmissionResponse)
def get_submission_by_user(
    user_id: int, current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a task Submission"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    tech_task = db.query(TechnicalTaskSubmission).filter(TechnicalTaskSubmission.user_id == user_id).first()

    if not tech_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task Submission not found for user with id {user_id}"
            )
    return tech_task
