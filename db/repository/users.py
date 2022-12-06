from sqlalchemy.orm import Session

from api.api_models.user_sign_up import UserSignUp
from db.models.users import User


def create_new_user(user: UserSignUp, db: Session):

    new_user = user.dict().copy()
    new_user.pop("password_confirmation")

    new_user = User(**new_user)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
