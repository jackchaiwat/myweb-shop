from fastapi import APIRouter, Request

router = APIRouter()

@router.post("/login")
async def login(request: Request):
    # ตรวจ JWT ของคุณตรงนี้
    request.session["user"] = "admin"
    return {"msg": "login success"}

@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return {"msg": "logout"}