from fastapi import FastAPI, HTTPException, UploadFile, status, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from database import engine, Base
import os
from datetime import datetime
from pathlib import Path
import shutil
# Models
from models.user import User
from models.product import Product
from models.category import Category
from models.order import Order, OrderDetail
from models.customer import Customer

# API
from api import user_api, product_api, order_api

# Admin
from sqladmin import Admin
from admin.admin_view import CategoryAdmin, ProductAdmin, UploadView
from admin.admin_auth import AdminAuth, SessionLocal
from api.admin_auth_api import router as admin_auth_router



# Auth
from auth.jwt_handler import create_access_token
if os.path.exists(".env"):
    load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")
ADMIN_SECRET_KEY = os.getenv("ADMIN_SECRET_KEY", SECRET_KEY)
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# ตรวจสอบว่า SECRET_KEY มีค่า (สำคัญ!)
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is not set!")
# =====================
# สร้าง app
# =====================
app = FastAPI(title="MyWeb Shop", version="1.0.0")

# =====================
# Database
# =====================

Base.metadata.create_all(bind=engine)

# =====================
# Middleware
# =====================
from dotenv import load_dotenv
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")

from fastapi.middleware.cors import CORSMiddleware


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:3000",
        "file://", 
        "*"  
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)


# =====================
# Static Files
# =====================
os.makedirs("static/uploads", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# =====================
# Admin 
# =====================
admin = Admin(
    app,
    engine,
    templates_dir="templates",
    authentication_backend=AdminAuth(secret_key=SECRET_KEY)
)

admin.add_view(ProductAdmin)
admin.add_view(UploadView)
admin.add_view(CategoryAdmin)
# =====================
# Routers
# =====================
app.include_router(user_api.router)
app.include_router(product_api.router)
app.include_router(order_api.router)
app.include_router(admin_auth_router)
# =====================
# Upload Endpoint
# =====================
@app.post("/upload-images")
async def upload_images(files: list[UploadFile] = File(...)):
    saved_files = []
    
    for file in files:
        if file.content_type.startswith('image/'):
            # สร้างชื่อไฟล์ unique
            ext = Path(file.filename).suffix
            filename = f"product_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
            filepath = f"static/uploads/{filename}"
            
            # บันทึกไฟล์
            content = await file.read()
            with open(filepath, "wb") as f:
                f.write(content)
            
            saved_files.append({
                "filename": filename,
                "url": f"/{filepath}"
            })
    
    return {"files": saved_files}

# =====================
# Login Endpoint
# =====================
@app.post("/api/login")
def login(username: str, password: str):
    if username == "admin" and password == "1234":
        token = create_access_token({"sub": username})
        return {
            "access_token": token,
            "token_type": "bearer"
        }
    
    raise HTTPException(
        status_code=401,
        detail="Invalid username or password"
    )

@app.get("/")
def root():
    return {
        "message": "MyWeb Shop API",
        "docs": "/docs",
        "admin": "/admin"
    }
# =====================
# Upload Images Endpoint
# =====================
@app.post("/upload-image-ajax")
async def upload_image_ajax(files: list[UploadFile] = File(...)):
    saved_urls = []
    
    for file in files:
        if file.content_type.startswith('image/'):
            # สร้างชื่อไฟล์ unique
            ext = Path(file.filename).suffix
            filename = f"product_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
            filepath = f"static/uploads/{filename}"
            
            # บันทึกไฟล์
            content = await file.read()
            with open(filepath, "wb") as f:
                f.write(content)
            
            saved_urls.append(f"/{filepath}")
    
    return {"url": saved_urls[0] if saved_urls else None, "urls": saved_urls}

# หรือใช้ Redirect กลับไปหน้า admin
@app.post("/upload-images-redirect")
async def upload_images_redirect(files: list[UploadFile]):
    saved_files = []
    
    for file in files:
        if file.content_type.startswith('image/'):
            ext = Path(file.filename).suffix
            filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
            file_path = f"static/uploads/{filename}"
            
            content = await file.read()
            with open(file_path, "wb") as f:
                f.write(content)
            
            saved_files.append(filename)
    
    # Redirect กลับไปที่ admin upload page
    return RedirectResponse(
        f"/admin/upload?uploaded={','.join(saved_files)}",
        status_code=status.HTTP_303_SEE_OTHER
    )
from starlette.middleware.base import BaseHTTPMiddleware
import re

class AddUploadFeatureMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        if request.method == 'POST':
            return response
        # ตรวจสอบว่าเป็นหน้า create หรือ edit สินค้า
        path = request.url.path
        
        # ใช้ regex เพื่อจับทั้ง /admin/product/create และ /admin/product/edit/xxx
        is_create = path == '/admin/product/create'
        is_edit = re.match(r'/admin/product/edit/\d+', path) is not None
        
        if is_create or is_edit:
            # อ่าน HTML
            body = b""
            async for chunk in response.body_iterator:
                body += chunk
            html = body.decode('utf-8')
            
            # JavaScript สำหรับอัปโหลดรูป
            script = """
            <script>
            document.addEventListener('DOMContentLoaded', function() {
                // จัดการอัปโหลดรูป
                const imageInput = document.querySelector('input[name="image"]');
                if (imageInput) {
                    const imageFieldGroup = imageInput.closest('.mb-3');
                    const currentImageUrl = imageInput.value;
                    
                    // สร้าง div สำหรับอัปโหลดรูป
                    const uploadDiv = document.createElement('div');
                    uploadDiv.className = 'mb-3';
                    uploadDiv.innerHTML = `
                        <label class="form-label fw-bold">
                            <i class="fas fa-image me-2"></i>อัปโหลดรูปภาพ
                        </label>
                        <div class="image-upload-area" id="uploadArea">
                            <i class="fas fa-cloud-upload-alt fa-2x mb-2" style="color: #667eea;"></i>
                            <p class="mb-1"><strong>คลิกเพื่อเลือกรูปภาพ</strong></p>
                            <p class="text-muted small">หรือลากรูปมาวางที่นี่</p>
                            <input type="file" id="productImage" accept="image/*" style="display: none;">
                            <div id="imagePreview" class="mt-2"></div>
                            <small class="text-muted">รองรับ .jpg, .png, .gif, .webp (ไม่เกิน 5MB)</small>
                        </div>
                        <hr>
                    `;
                    
                    // แทรกก่อนช่อง image
                    if (imageFieldGroup) {
                        imageFieldGroup.parentNode.insertBefore(uploadDiv, imageFieldGroup);
                        
                        if (currentImageUrl && currentImageUrl !== '') {
                            const currentDiv = document.createElement('div');
                            currentDiv.className = 'mb-3';
                            
                            
                            let imgUrl = currentImageUrl;
                            if (!imgUrl.startsWith('/')) {
                                imgUrl = '/' + imgUrl;
                            }
                            
                            if (imgUrl.indexOf('//') === 0) {
                                imgUrl = imgUrl.substring(1);
                            }
                            
                            
                            let fileName = currentImageUrl.split('/').pop();
                            
                            currentDiv.innerHTML = `
                                <label class="form-label">รูปปัจจุบัน</label>
                                <div>
                                    <img src="${imgUrl}" 
                                        style="max-width: 150px; border-radius: 8px; border: 1px solid #ddd;"
                                        onerror="this.style.display='none'; this.parentElement.innerHTML+='<span style=\'color:#999;font-size:12px;\'>ไม่พบรูป</span>'">
                                    <div class="mt-1"><small class="text-muted">${fileName}</small></div>
                                </div>
                            `;
                            imageFieldGroup.parentNode.insertBefore(currentDiv, imageFieldGroup);
                        }
                    }
                    
                    const fileInput = document.getElementById('productImage');
                    const preview = document.getElementById('imagePreview');
                    const uploadArea = document.getElementById('uploadArea');
                    
                    // คลิกเพื่อเลือกรูป
                    uploadArea.addEventListener('click', function() {
                        fileInput.click();
                    });
                    
                    fileInput.addEventListener('change', async function(e) {
                        const file = e.target.files[0];
                        if (!file) return;
                        
                        if (file.size > 5 * 1024 * 1024) {
                            alert('ไฟล์มีขนาดใหญ่เกิน 5MB');
                            return;
                        }
                        
                        // Preview
                        const reader = new FileReader();
                        reader.onload = function(ev) {
                            preview.innerHTML = `
                                <img src="${ev.target.result}" style="max-width: 150px; border-radius: 8px;">
                                <div class="mt-1"><span class="badge bg-info">${file.name}</span></div>
                            `;
                        };
                        reader.readAsDataURL(file);
                        
                        preview.innerHTML += `<div class="mt-2"><div class="spinner-border spinner-border-sm text-primary"></div> กำลังอัปโหลด...</div>`;
                        
                        const formData = new FormData();
                        formData.append('files', file);
                        
                        try {
                            const response = await fetch('/upload-images', {
                                method: 'POST',
                                body: formData
                            });
                            
                            const result = await response.json();
                            
                            if (result.files && result.files.length > 0) {
                                imageInput.value = result.files[0].url;
                                preview.innerHTML += `<div class="text-success mt-1">✅ อัปโหลดสำเร็จ!</div>`;
                                setTimeout(() => {
                                    const msg = preview.querySelector('.text-success');
                                    if (msg) msg.remove();
                                }, 3000);
                            } else {
                                preview.innerHTML += `<div class="text-danger mt-1">❌ อัปโหลดล้มเหลว</div>`;
                            }
                        } catch (error) {
                            preview.innerHTML += `<div class="text-danger mt-1">❌ อัปโหลดล้มเหลว</div>`;
                        }
                    });
                    
                    // Drag & Drop
                    uploadArea.addEventListener('dragover', function(e) {
                        e.preventDefault();
                        this.style.borderColor = '#667eea';
                        this.style.background = '#f0f0ff';
                    });
                    
                    uploadArea.addEventListener('dragleave', function(e) {
                        e.preventDefault();
                        this.style.borderColor = '#ddd';
                        this.style.background = '#fafafa';
                    });
                    
                    uploadArea.addEventListener('drop', function(e) {
                        e.preventDefault();
                        this.style.borderColor = '#ddd';
                        this.style.background = '#fafafa';
                        const file = e.dataTransfer.files[0];
                        if (file && file.type.startsWith('image/')) {
                            fileInput.files = e.dataTransfer.files;
                            fileInput.dispatchEvent(new Event('change'));
                        }
                    });
                }
            });
            </script>
            """
            
            # CSS
            css = """
            <style>
            .image-upload-area {
                border: 2px dashed #ddd;
                border-radius: 10px;
                padding: 20px;
                text-align: center;
                cursor: pointer;
                transition: all 0.3s;
                background: #fafafa;
            }
            .image-upload-area:hover {
                border-color: #667eea;
                background: #f0f0ff;
            }
            </style>
            """
            
            # แทรก CSS และ JavaScript
            html = html.replace('</head>', f'{css}</head>')
            html = html.replace('</body>', f'{script}</body>')
            
            from fastapi.responses import HTMLResponse
            return HTMLResponse(content=html, status_code=response.status_code)
        
        return response

# เพิ่ม middleware
app.add_middleware(AddUploadFeatureMiddleware)

from models.category import Category


@app.get("/api/categories")
async def get_categories():
    db = SessionLocal()
    try:
        categories = db.query(Category).all()
        return [
            {"id": cat.id, "name": cat.name} 
            for cat in categories
        ]
    finally:
        db.close()
from starlette.middleware.base import BaseHTTPMiddleware


