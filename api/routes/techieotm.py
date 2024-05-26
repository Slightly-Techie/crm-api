from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import desc, extract, select
from fastapi_pagination.links import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.orm import Session
from api.api_models.user import TechieOTMCreate, TechieOTMResponse
from db.database import get_db
from utils.permissions import is_admin
from db.models.users import User
from db.models.techie_of_the_month import TechieOTM


techieotm_router = APIRouter(tags=["User"], prefix="/users/techieotm")


@techieotm_router.post("/", status_code=status.HTTP_201_CREATED, response_model=TechieOTMResponse)
def create_techie_of_the_month(
    techieotm: TechieOTMCreate, current_user=Depends(is_admin),
    db: Session = Depends(get_db)
):
    current_month = datetime.now().month
    current_year = datetime.now().year

    existing_techieotm = db.query(TechieOTM).filter(
        extract("month", TechieOTM.created_at) == current_month, extract(
            "year", TechieOTM.created_at) == current_year).first()
    if existing_techieotm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Techie of the Month already posted for the current month")

    user = db.query(User).filter(User.id == techieotm.user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    new_techieotm = TechieOTM(**techieotm.model_dump())

    db.add(new_techieotm)
    db.commit()
    db.refresh(new_techieotm)

    techieotm_response = TechieOTMResponse(
        id=new_techieotm.id,
        user=user,
        points=new_techieotm.points,
        created_at=new_techieotm.created_at,
    )

    return techieotm_response


@techieotm_router.get("/latest", response_model=TechieOTMResponse)
def get_latest_techie_of_the_month(db: Session = Depends(get_db)):
    latest_techieotm = db.query(TechieOTM).order_by(TechieOTM.created_at.desc()).first()
    if not latest_techieotm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Techie of the Month found")

    user = db.query(User).filter(User.id == latest_techieotm.user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    techieotm_response = TechieOTMResponse(
        id=latest_techieotm.id,
        user=user,
        points=latest_techieotm.points,
        created_at=latest_techieotm.created_at,
    )

    return techieotm_response


@techieotm_router.get("/", response_model=Page[TechieOTMResponse])
def get_all_techies_of_the_months(db: Session = Depends(get_db)):
    return paginate(db, select(TechieOTM).order_by(desc(TechieOTM.created_at)))
