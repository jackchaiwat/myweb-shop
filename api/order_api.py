from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import SessionLocal
from crud.order_crud import create_order
from schemas.order_schema import OrderCreate

router = APIRouter(prefix="/orders")

def get_db():

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.post("/")
def create(data: OrderCreate, db: Session = Depends(get_db)):

    return create_order(db, data.user_id)