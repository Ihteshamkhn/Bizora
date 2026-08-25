"""Business management API."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from api.deps import get_current_user, get_business_owned
from database.connection import get_db
from database.models import Business, User

router = APIRouter(prefix="/api/businesses", tags=["businesses"])


class BusinessCreate(BaseModel):
    name: str
    business_type: str | None = None
    currency: str = "PKR"


class BusinessOut(BaseModel):
    id: int
    name: str
    business_type: str | None
    currency: str

    class Config:
        from_attributes = True


@router.post("", response_model=BusinessOut)
def create_business(body: BusinessCreate,
                    db: Session = Depends(get_db),
                    user: User = Depends(get_current_user)):
    business = Business(owner_id=user.id, **body.model_dump())
    db.add(business)
    db.commit()
    return business


@router.get("", response_model=list[BusinessOut])
def list_businesses(db: Session = Depends(get_db),
                    user: User = Depends(get_current_user)):
    return db.query(Business).filter(Business.owner_id == user.id).all()


@router.get("/{business_id}", response_model=BusinessOut)
def get_business(business: Business = Depends(get_business_owned)):
    return business
