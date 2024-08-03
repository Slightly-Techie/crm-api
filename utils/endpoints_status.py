from db.database import get_db
from db.models.endpoints import Endpoints
from fastapi import HTTPException, status


def check_endpoint(endpoint: str):
    db = next(get_db())
    endpoint_query = db.query(Endpoints).filter(Endpoints.endpoint == endpoint).first()
    if endpoint_query:
        if not endpoint_query.status:
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail=f"{endpoint.upper()} is closed")
        else:
            return True
    else:
        create_signup_endpoint(status=True)
        return check_endpoint("signup")


def endpoint_status_dependency(endpoint: str):
    return lambda: check_endpoint(endpoint)


def create_signup_endpoint(status: str = False):
    db = next(get_db())
    signup_endpoint_object = {
        "endpoint": "signup",
        "status": status
    }
    signup_obj = db.query(Endpoints).filter(Endpoints.endpoint == signup_endpoint_object["endpoint"])
    if signup_obj.first():
        pass
    else:
        signup_object = Endpoints(
            endpoint=signup_endpoint_object["endpoint"],
            status=signup_endpoint_object["status"]
            )
        db.add(signup_object)
        db.commit()
