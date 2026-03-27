from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from crud.user_crud import create_user, get_user_by_username
from database import SessionLocal
from schemas.user_schema import UserCreate, UserLogin
from auth.jwt_handler import verify_password, create_access_token

router = APIRouter(prefix="/users", tags=["Users"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    return create_user(db, user.username, user.email, user.password)

@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = get_user_by_username(db, user.username)
    
    if not db_user:
        return {"error": "user not found"}
    
    if not verify_password(user.password, db_user.password):
        return {"error": "wrong password"}
    
    token = create_access_token({"user_id": db_user.id})
    
    return {
        "access_token": token,
        "token_type": "bearer"
    }