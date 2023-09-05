from fastapi import APIRouter, Depends, HTTPException, status
from api.api_models.tags import TagCreate
from api.api_models.user import Tags
from db.database import get_db
from sqlalchemy.orm import Session, joinedload
from db.models.users import User
from db.models.tags import Tag
from db.models.users_tags import UserTag

from utils.oauth2 import get_current_user



tag_route = APIRouter(tags=["User"], prefix='/users')


@tag_route.get("/tags")
def get_current_user_tags(user=Depends(get_current_user), db:Session = Depends(get_db)):
    db_query =  db.query(User).filter(User.id == user.id).\
        options(joinedload(User.tags)).first()   
    return {"tags": db_query.tags}

@tag_route.post('/tags', response_model=Tags, status_code=status.HTTP_201_CREATED)
def create_tag(tag: TagCreate, current_user=Depends(get_current_user), 
        db:Session=Depends(get_db)):
    if not current_user:
        raise HTTPException(status_code=401, detail='Unauthorized')

    user_tag = db.query(Tag).filter(Tag.name == Tag.name).first()
    if user_tag:
        if user_tag in current_user.tags:
            raise HTTPException(status_code=400, detail='Tag already exists for user')
        else:
            current_user.tags.append(user_tag)
            db.commit()
            return user_tag
    else:
        user_tag = Tag(name=tag.name)
        db.add(user_tag)
        db.commit()
        db.refresh(user_tag)

        current_user.tags.append(user_tag)
        db.commit()

        return user_tag

@tag_route.delete("/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag_by_id(tag_id: int, user=Depends(get_current_user), db:Session = Depends(get_db)):
    user_tag =  db.query(UserTag).filter(UserTag.tag_id == tag_id)
    tag = user_tag.first()

    if not tag:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                             detail=f'No tag with this id: {tag_id} found')
    
    user_tag.delete(synchronize_session=False)
    db.commit()
