from fastapi import HTTPException, status

from db.models.tags import Tag
from db.models.users import User
from db.repository.tags import TagRepository


class TagService:
    def __init__(self, tag_repo: TagRepository):
        self.tag_repo = tag_repo

    def get_user_tags(self, user: User) -> dict:
        tags = self.tag_repo.get_all_for_user(user.id)
        return {"tags": tags}

    def create_tag(self, user: User, tag_name: str) -> Tag:
        existing_tag = self.tag_repo.get_by_name(tag_name)
        if existing_tag:
            if existing_tag in user.tags:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tag already exists for user")
            self.tag_repo.add_to_user(user, existing_tag)
            return existing_tag
        new_tag = self.tag_repo.create(tag_name)
        self.tag_repo.add_to_user(user, new_tag)
        return new_tag

    def delete_tag(self, tag_id: int) -> None:
        entry = self.tag_repo.get_user_tag_entry(tag_id)
        if not entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No tag with this id: {tag_id} found"
            )
        self.tag_repo.delete_user_tag(tag_id)
