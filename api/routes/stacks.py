from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from api.api_models import stacks as stack_schemas
from db.database import get_db
from db.models.users import User
from db.repository.stacks import StackRepository
from services.stack_service import StackService
from utils.permissions import is_admin, user_accepted

stack_router = APIRouter(tags=["Stacks"], prefix="/stacks")


def _service(db: Session) -> StackService:
    return StackService(StackRepository(db))


@stack_router.get("/", response_model=list[stack_schemas.Stacks])
async def list_stacks(db: Session = Depends(get_db), page: int = 1, limit: int = 100,
                      current_user=Depends(user_accepted)):
    return _service(db).list_stacks(page=page, limit=limit)


@stack_router.post("/", response_model=stack_schemas.Stacks, status_code=status.HTTP_201_CREATED)
async def create_stack(stack: stack_schemas.StackCreate, user: User = Depends(is_admin),
                       db: Session = Depends(get_db)):
    return _service(db).create(stack.name)


@stack_router.get("/{stack_id}", response_model=stack_schemas.Stacks)
async def read_stack(stack_id: int, db: Session = Depends(get_db),
                     current_user=Depends(user_accepted)):
    return _service(db).get_by_id(stack_id)


@stack_router.patch("/{stack_id}", response_model=stack_schemas.Stacks)
async def update_stack(stack_id: int, payload: stack_schemas.StackCreate,
                       user: User = Depends(is_admin), db: Session = Depends(get_db)):
    return _service(db).update(stack_id, payload.model_dump(exclude_unset=True))


@stack_router.delete("/{stack_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_stack(stack_id: int, user: User = Depends(is_admin), db: Session = Depends(get_db)):
    _service(db).delete(stack_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
