from sqlalchemy.orm import Session


class BaseRepository:
    model = None

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, id: int):
        return self.db.query(self.model).filter(self.model.id == id).first()

    def save(self, obj):
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete_obj(self, obj):
        self.db.delete(obj)
        self.db.commit()

    def commit(self):
        self.db.commit()

    def rollback(self):
        self.db.rollback()

    def refresh(self, obj):
        self.db.refresh(obj)
