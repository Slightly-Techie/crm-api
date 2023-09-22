from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import desc, extract
from sqlalchemy.orm import Session
from api.api_models.user import TechieOTMCreate, TechieOTMPaginated, TechieOTMResponse
from db.database import get_db
from utils.permissions import is_admin
from db.models.users import User
from db.models.techie_of_the_month import TechieOTM


techieotm_router = APIRouter(tags=["User"], prefix="/users/techieotm")


@techieotm_router.post("/", status_code=status.HTTP_201_CREATED, response_model=TechieOTMResponse)
def create_techie_of_the_month(techieotm: TechieOTMCreate, current_user=Depends(is_admin), db: Session = Depends(get_db)):
    current_month =datetime.now().month
    current_year = datetime.now().year

    existing_techieotm = db.query(TechieOTM).filter(extract("month", TechieOTM.created_at) == current_month, extract("year", TechieOTM.created_at) == current_year).first()
    if existing_techieotm:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Techie of the Month already posted for the current month")

    user = db.query(User).filter(User.id == techieotm.user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    new_techieotm = TechieOTM(**techieotm.dict())

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


@techieotm_router.get("/", response_model=TechieOTMPaginated)
def get_all_techies_of_the_months(limit: int = Query(default=50, ge=1, le=100), page: int = Query(default=1, ge=1), db: Session = Depends(get_db)):
    total_techies = db.query(TechieOTM).count()
    pages = (total_techies - 1) // limit + 1
    offset = (page - 1) * limit
    techiesotm = db.query(TechieOTM).order_by(desc(TechieOTM.created_at)).offset(offset).limit(limit).all()

    links = {
        "first": f"/api/v1/users/techieotm/?limit={limit}&page=1",
        "last": f"/api/v1/users/techieotm/?limit={limit}&page={pages}",
        "self": f"/api/v1/users/techieotm/?limit={limit}&page={page}",
        "next": None,
        "prev": None,
    }

    if page < pages:
        links["next"] = f"/api/v1/users/techieotm/?limit={limit}&page={page + 1}"

    if page > 1:
        links["prev"] = f"/api/v1/users/techieotm/?limit={limit}&page={page - 1}"

    return TechieOTMPaginated(
        techies=techiesotm,
        total=total_techies,
        page=page,
        size=limit,
        pages=pages,
        links=links,
    )

