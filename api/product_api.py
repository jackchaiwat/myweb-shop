from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal
from schemas.product_schema import Product, ProductCreate
from crud.product_crud import create_product, get_products

router = APIRouter(prefix="/products", tags=["Products"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=Product)
def create(data: ProductCreate, db: Session = Depends(get_db)):
    return create_product(db, data)

@router.get("/", response_model=List[Product])
def list_products(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return get_products(db, skip, limit)

@router.get("/list", response_model=List[Product])
def product_list(db: Session = Depends(get_db)):
    """Get all products list"""
    return get_products(db, 0, 100)