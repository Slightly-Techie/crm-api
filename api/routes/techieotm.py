from fastapi import APIRouter, Depends, status
from fastapi_pagination.ext.sqlalchemy import paginate
from fastapi_pagination.links import Page
from sqlalchemy.orm import Session

from api.api_models.user import TechieOTMCreate, TechieOTMResponse
from db.database import get_db
from db.repository.techieotm import TechieOTMRepository
from db.repository.users import UserRepository
from services.techieotm_service import TechieOTMService
from utils.permissions import is_admin

techieotm_router = APIRouter(tags=["User"], prefix="/users/techieotm")


def _service(db: Session) -> TechieOTMService:
    return TechieOTMService(TechieOTMRepository(db), UserRepository(db))


@techieotm_router.post("/", status_code=status.HTTP_201_CREATED, response_model=TechieOTMResponse)
def create_techie_of_the_month(
    techieotm: TechieOTMCreate, current_user=Depends(is_admin),
    db: Session = Depends(get_db)
):
    return _service(db).create(techieotm.user_id, techieotm.points)


@techieotm_router.get("/latest", response_model=TechieOTMResponse)
def get_latest_techie_of_the_month(db: Session = Depends(get_db)):
    return _service(db).get_latest()


@techieotm_router.get("/", response_model=Page[TechieOTMResponse])
def get_all_techies_of_the_months(db: Session = Depends(get_db)):
    return paginate(db, _service(db).get_all_query())
