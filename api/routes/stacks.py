from fastapi import APIRouter, Depends, HTTPException, status, Response
from api.api_models import stacks as stack_schemas
from utils.permissions import is_admin

from db.database import get_db
from sqlalchemy.orm import Session
from db.models.users import User
from db.models.stacks import Stack


stack_router = APIRouter(tags=["Stacks"], prefix="/stacks")


# Return all stacks
@stack_router.get("/", response_model=list[stack_schemas.Stacks])
async def list_stacks(db: Session = Depends(get_db), page: int = 1, limit: int = 100):
    # calculate skip value
    page = page if page >= 1 else 1
    skip = (page - 1) * limit

    stacks = db.query(Stack).offset(skip).limit(limit).all()
    return stacks


# create a new Stack
@stack_router.post(
    "/", response_model=stack_schemas.Stacks, status_code=status.HTTP_201_CREATED
)
async def create_stack(
    stack: stack_schemas.StackCreate,
    user: User = Depends(is_admin),
    db: Session = Depends(get_db),
):
    new_stack = Stack(**dict(stack))
    try:
        db.add(new_stack)
        db.commit()
        db.refresh(new_stack)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.__str__())

    return new_stack


# read stack with id
@stack_router.get("/{stack_id}", response_model=stack_schemas.Stacks)
async def read_stack(stack_id: int, db: Session = Depends(get_db)):
    stack = db.query(Stack).filter(Stack.id == stack_id).first()

    if not stack:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Stack not found"
        )

    return stack


# update stack
@stack_router.patch("/{stack_id}", response_model=stack_schemas.Stacks)
async def update_stack(
    stack_id: int,
    payload: stack_schemas.StackCreate,
    user: User = Depends(is_admin),
    db: Session = Depends(get_db),
):
    stack_query = db.query(Stack).filter(Stack.id == stack_id)
    old_stack = stack_query.first()

    if not old_stack:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Stack not found"
        )
    try:
        stack_query.update(payload.model_dump(exclude_unset=True))
        db.commit()
        db.refresh(old_stack)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=dict(e.__str__())
        )

    return old_stack


# delete stack
@stack_router.delete("/{stack_id}", response_model=stack_schemas.Stacks)
async def delete_stack(
    stack_id: int, user: User = Depends(is_admin), db: Session = Depends(get_db)
):
    stack_query = db.query(Stack).filter(Stack.id == stack_id)
    old_stack = stack_query.first()

    if not old_stack:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Stack not found"
        )

    stack_query.delete()
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
