from typing import Optional

from sqlalchemy.orm import Session

from db.models.stacks import Stack
from db.repository.base import BaseRepository


class StackRepository(BaseRepository):
    model = Stack

    def list(self, page: int = 1, limit: int = 100) -> list[Stack]:
        page = page if page >= 1 else 1
        skip = (page - 1) * limit
        return self.db.query(Stack).offset(skip).limit(limit).all()

    def create(self, name: str) -> Stack:
        new_stack = Stack(name=name)
        return self.save(new_stack)

    def update(self, stack: Stack, payload: dict) -> Stack:
        query = self.db.query(Stack).filter(Stack.id == stack.id)
        query.update(payload)
        self.db.commit()
        self.db.refresh(stack)
        return stack

    def delete_by_id(self, stack: Stack) -> None:
        self.db.query(Stack).filter(Stack.id == stack.id).delete()
        self.db.commit()
