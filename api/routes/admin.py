from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List
from models import User
from database import get_db

admin = APIRouter(tags=["admin"])

@admin.get('/users/')
def get_all_users(db: Session = Depends(get_db), limit: int=50, offset: int=0) -> List[None] | List[User]:

    return db.scalars(select(User).offset(offset).limit(limit)).all()