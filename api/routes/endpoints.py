from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.api_models.endpoints import EndpointBase
from db.database import get_db
from db.models.users import User
from db.repository.endpoints import EndpointRepository
from services.endpoint_service import EndpointService
from utils.permissions import is_admin

endpoints_route = APIRouter(prefix="/endpoints", tags=["Endpoints"])


def _service(db: Session) -> EndpointService:
    return EndpointService(EndpointRepository(db))


@endpoints_route.post("/")
async def add_endpoint_status(endpoint: EndpointBase, db: Session = Depends(get_db),
                              user: User = Depends(is_admin)):
    _service(db).add_endpoint(endpoint.endpoint)


@endpoints_route.put("/")
async def toggle_endpoint(endpoint: EndpointBase, db: Session = Depends(get_db),
                          user: User = Depends(is_admin)):
    _service(db).toggle_endpoint(endpoint.endpoint)
