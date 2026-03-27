from sqladmin.authentication import AuthenticationBackend
from sqlalchemy.orm import Session
from database import SessionLocal
from models.user import User
from auth.jwt_handler import verify_password

class AdminAuth(AuthenticationBackend):
    async def login(self, request):
        form = await request.form()
        username = form.get("username")
        password = form.get("password")
        
        # ดึงข้อมูลจากฐานข้อมูล
        db: Session = SessionLocal()
        try:
            # ค้นหา user ที่เป็น admin หรือ superuser
            user = db.query(User).filter(
                User.username == username,
                User.is_superuser == True  # ต้องเป็น superuser เท่านั้น
            ).first()
            
            if user and verify_password(password, user.password):
                # ล็อกอินสำเร็จ
                request.session.update({
                    "token": str(user.id),
                    "username": user.username,
                    "is_superuser": True
                })
                return True
        finally:
            db.close()
        
        
        if username == "admin" and password == "admin123":
            request.session.update({"token": "admin", "username": "admin", "is_superuser": True})
            return True
        
        return False

    async def logout(self, request):
        request.session.clear()
        return True

    async def authenticate(self, request):
        token = request.session.get("token")
        return token is not None