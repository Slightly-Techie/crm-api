from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from db.database import get_db
from db.models.endpoints import Endpoints
from db.models.users import User
from utils.permissions import is_admin

from api.api_models.endpoints import EndpointBase


endpoints_route = APIRouter(prefix="/endpoints", tags=["Endpoints"])


@endpoints_route.post("/")
async def add_endpoint_status(endpoint: EndpointBase, db: Session = Depends(get_db), user: User = Depends(is_admin)):
    endpoint_query = db.query(Endpoints).filter(Endpoints.endpoint == endpoint.endpoint).first()
    if endpoint_query:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Endpoint already exists")

    new_endpoint = Endpoints(endpoint=endpoint.endpoint, status=True)
    db.add(new_endpoint)
    db.commit()


@endpoints_route.put("/")
async def toggle_endpoint(endpoint: EndpointBase, db: Session = Depends(get_db), user: User = Depends(is_admin)):
    print(endpoint.endpoint)
    endpoint_query = db.query(Endpoints).filter(Endpoints.endpoint == endpoint.endpoint).first()
    if not endpoint_query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Endpoint {endpoint.endpoint} not found")

    if endpoint_query.status:
        endpoint_query.status = False
    else:
        endpoint_query.status = True
    endpoint_query.toggled_at = datetime.now()

    db.commit()
