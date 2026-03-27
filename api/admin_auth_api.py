from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional

from core.dependencies import get_current_admin_user
from database import SessionLocal
from models.user import User
from auth.jwt_handler import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/admin-auth", tags=["Admin Authentication"])

# ===================== Schemas =====================
class AdminRegister(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class AdminLogin(BaseModel):
    username: str
    password: str

class AdminResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    is_superuser: bool
    
    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: AdminResponse

# ===================== Database Dependency =====================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ===================== API Endpoints =====================
@router.post("/register", response_model=AdminResponse, status_code=status.HTTP_201_CREATED)
def register_admin(user_data: AdminRegister, db: Session = Depends(get_db)):
    """
    ลงทะเบียน Admin ใหม่
    """
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
 
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    new_admin = User(
        username=user_data.username,
        email=user_data.email,
        password=hash_password(user_data.password),
        full_name=user_data.full_name,
        is_superuser=True,  
        is_active=True
    )
    
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)
    
    return new_admin

@router.post("/login", response_model=TokenResponse)
def login_admin(login_data: AdminLogin, db: Session = Depends(get_db)):
    """
    เข้าสู่ระบบสำหรับ Admin
    """
    user = db.query(User).filter(
        User.username == login_data.username,
        User.is_superuser == True 
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # ตรวจสอบรหัสผ่าน
    if not verify_password(login_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
   
    token_data = {
        "sub": user.username,
        "user_id": user.id,
        "is_superuser": user.is_superuser
    }
    access_token = create_access_token(token_data)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@router.get("/me", response_model=AdminResponse)
def get_current_admin(
    current_user: User = Depends(get_current_admin_user)  
):
    """
    ดูข้อมูล Admin ที่ใครกำลังล็อกอินอยู่  ก้อปปี้ token หลังจาก login มาใส่ใน Authorize บนขวาบนของ Swagger แล้วกด excute 
/admin-auth/me เพื่อดูข้อมูลของ admin ที่ล็อกอินอยู่
    """
    return current_user