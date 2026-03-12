from datetime import datetime
from typing import Optional

from sqlalchemy import desc, extract, select
from sqlalchemy.orm import selectinload

from db.models.techie_of_the_month import TechieOTM
from db.repository.base import BaseRepository


class TechieOTMRepository(BaseRepository):
    model = TechieOTM

    def get_for_current_month(self) -> Optional[TechieOTM]:
        now = datetime.now()
        return self.db.query(TechieOTM).filter(
            extract("month", TechieOTM.created_at) == now.month,
            extract("year", TechieOTM.created_at) == now.year
        ).first()

    def get_latest(self) -> Optional[TechieOTM]:
        return self.db.query(TechieOTM).order_by(TechieOTM.created_at.desc()).first()

    def create(self, user_id: int, points: int) -> TechieOTM:
        entry = TechieOTM(user_id=user_id, points=points)
        return self.save(entry)

    def get_all_paginated_query(self):
        return select(TechieOTM).options(selectinload(TechieOTM.user)).order_by(desc(TechieOTM.created_at))
