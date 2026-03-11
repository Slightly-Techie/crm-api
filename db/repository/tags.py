from typing import Optional

from sqlalchemy.orm import Session, joinedload

from db.models.tags import Tag
from db.models.users import User
from db.models.users_tags import UserTag
from db.repository.base import BaseRepository


class TagRepository(BaseRepository):
    model = Tag

    def get_all_for_user(self, user_id: int) -> list[Tag]:
        user = self.db.query(User).filter(User.id == user_id).options(
            joinedload(User.tags)
        ).first()
        return user.tags if user else []

    def get_by_name(self, name: str) -> Optional[Tag]:
        return self.db.query(Tag).filter(Tag.name == name).first()

    def create(self, name: str) -> Tag:
        tag = Tag(name=name)
        return self.save(tag)

    def add_to_user(self, user: User, tag: Tag) -> None:
        user.tags.append(tag)
        self.db.commit()

    def get_user_tag_entry(self, tag_id: int) -> Optional[UserTag]:
        return self.db.query(UserTag).filter(UserTag.tag_id == tag_id).first()

    def delete_user_tag(self, tag_id: int) -> None:
        query = self.db.query(UserTag).filter(UserTag.tag_id == tag_id)
        query.delete(synchronize_session=False)
        self.db.commit()
