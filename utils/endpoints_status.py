from db.database import get_db
from db.models.endpoints import Endpoints
from fastapi import HTTPException, status


def check_endpoint(endpoint: str):
    db = next(get_db())
    endpoint_query = db.query(Endpoints).filter(Endpoints.endpoint == endpoint).first()
    
    if not endpoint_query.status:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail=f"{endpoint.upper()} is closed")


def endpoint_status_dependency(endpoint: str):
    return lambda: check_endpoint(endpoint)
