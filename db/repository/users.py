from sqlalchemy.orm import Session

from api.api_models.user_sign_up import UserSignUp
from db.models.users import User


def create_new_user(user: UserSignUp, db: Session):

    new_user = User(**user)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
