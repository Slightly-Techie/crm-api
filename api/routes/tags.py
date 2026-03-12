from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from api.api_models.tags import TagCreate
from api.api_models.user import Tags
from db.database import get_db
from db.repository.tags import TagRepository
from services.tag_service import TagService
from utils.oauth2 import get_current_user

tag_route = APIRouter(tags=["User"], prefix="/users")


def _service(db: Session) -> TagService:
    return TagService(TagRepository(db))


@tag_route.get("/tags")
def get_current_user_tags(user=Depends(get_current_user), db: Session = Depends(get_db)):
    return _service(db).get_user_tags(user)


@tag_route.post("/tags", response_model=Tags, status_code=status.HTTP_201_CREATED)
def create_tag(tag: TagCreate, current_user=Depends(get_current_user),
               db: Session = Depends(get_db)):
    return _service(db).create_tag(current_user, tag.name)


@tag_route.delete("/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag_by_id(tag_id: int, user=Depends(get_current_user),
                     db: Session = Depends(get_db)):
    _service(db).delete_tag(tag_id)
