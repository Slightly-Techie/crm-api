from datetime import datetime
from typing import Optional

from db.models.endpoints import Endpoints
from db.repository.base import BaseRepository


class EndpointRepository(BaseRepository):
    model = Endpoints

    def get_by_name(self, endpoint: str) -> Optional[Endpoints]:
        return self.db.query(Endpoints).filter(Endpoints.endpoint == endpoint).first()

    def create(self, endpoint: str, status: bool = True) -> Endpoints:
        obj = Endpoints(endpoint=endpoint, status=status)
        return self.save(obj)

    def toggle(self, endpoint_obj: Endpoints) -> Endpoints:
        endpoint_obj.status = not endpoint_obj.status
        endpoint_obj.toggled_at = datetime.now()
        self.db.commit()
        self.db.refresh(endpoint_obj)
        return endpoint_obj
