from sqladmin import ModelView, BaseView, expose
from models.product import Product
from models.category import Category
from fastapi import Request
from fastapi.responses import HTMLResponse
from markupsafe import Markup
import os
from models.user import User

class CategoryAdmin(ModelView, model=Category):
    name = "หมวดหมู่"
    name_plural = "หมวดหมู่สินค้า"
    icon = "fa-solid fa-tags"
    
    column_list = [Category.id, Category.name]
    column_labels = {
        Category.id: "รหัส",
        Category.name: "ชื่อหมวดหมู่"
    }
    column_searchable_list = [Category.name]
    column_sortable_list = [Category.id, Category.name]
    
    form_columns = [Category.name]
    
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True



class UserAdmin(ModelView, model=User):
    name = "ผู้ใช้"
    name_plural = "ผู้ใช้ทั้งหมด"
    icon = "fa-solid fa-users"
    
    column_list = [
        User.id,
        User.username,
        User.email,
        User.full_name,
        User.is_superuser,
        User.is_active,
        User.created_at,
    ]
    
    column_labels = {
        User.id: "รหัส",
        User.username: "ชื่อผู้ใช้",
        User.email: "อีเมล",
        User.full_name: "ชื่อ-นามสกุล",
        User.is_superuser: "ผู้ดูแลระบบ",
        User.is_active: "สถานะ",
        User.created_at: "วันที่สมัคร",
    }
    
    column_searchable_list = [User.username, User.email, User.full_name]
    column_sortable_list = [User.id, User.username, User.created_at]
    column_filters = [User.is_superuser, User.is_active]
    
    # ✅ แก้ไข: ใช้แค่ form_columns อย่างเดียว (ไม่ใช้ form_excluded_columns)
    form_columns = [
        User.username,
        User.email,
        User.password,
        User.full_name,
        User.is_superuser,
        User.is_active,
    ]
    
    # ✅ หรือ ใช้ form_excluded_columns อย่างเดียว
    # form_excluded_columns = [User.id, User.created_at, User.updated_at]
    
    # ✅ กำหนดให้แสดง checkbox สำหรับ boolean fields
    form_overrides = {
        "is_superuser": None,
        "is_active": None,
    }
    
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True
    
    async def on_model_change(self, data, model, is_created, request):
        """เข้ารหัสรหัสผ่านก่อนบันทึก"""
        from auth.jwt_handler import hash_password
        
        if "password" in data and data["password"]:
            model.password = hash_password(data["password"])
        return model


class ProductAdmin(ModelView, model=Product):
    name = "สินค้า"
    name_plural = "สินค้าทั้งหมด"
    icon = "fa-solid fa-box"
    
    column_list = [
        Product.id,
        Product.name,
        Product.price,
        Product.stock,
        Product.category,
        Product.image,
    ]
    
    column_labels = {
        Product.id: "รหัสสินค้า",
        Product.name: "ชื่อสินค้า",
        Product.price: "ราคา",
        Product.stock: "จำนวนในสต็อก",
        Product.category: "ประเภทสินค้า",
        Product.image: "รูปสินค้า"
    }
    
    column_searchable_list = [Product.name]
    column_sortable_list = [Product.id, Product.name, Product.price]
    

    form_columns = [
        Product.name,
        Product.price,
        Product.stock,
        Product.category,
        Product.image,
    ]
    
    column_formatters = {
    Product.image: lambda m, a: Markup(f'''
        <div style="
            width: 50px;
            height: 50px;
            border-radius: 8px;
            overflow: hidden;
            background: #f5f5f5;
            display: flex;
            align-items: center;
            justify-content: center;
        ">
            <img src="/static/uploads/{m.image.split('/')[-1]}" style="
                width: 100%;
                height: 100%;
                object-fit: cover;
            ">
        </div>
    ''') if m.image else Markup('<div style="width: 50px; height: 50px; background: #f5f5f5; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: #999; font-size: 12px;">ไม่มีรูป</div>'),
    Product.category: lambda m, a: m.category.name if m.category else "-"
}
    
    column_formatters_detail = {
        Product.image: lambda m, a: Markup(f'<img src="/{m.image}" style="max-width: 200px;">') if m.image else '-'
    }
    
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True
    
    async def after_model_change(self, data, model, is_created, request):
        request.session["flash"] = "บันทึกสินค้าสำเร็จ"

class UploadView(BaseView):
    name = "อัปโหลดรูปภาพ"
    icon = "fa-solid fa-upload"
    
    @expose("/upload", methods=["GET"])
    async def upload_page(self, request: Request) -> HTMLResponse:
        uploaded = request.query_params.get("uploaded", "")
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>อัปโหลดรูปภาพสินค้า</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        </head>
        <body>
            <div class="container mt-5">
                <div class="row">
                    <div class="col-md-8 mx-auto">
                        <div class="card">
                            <div class="card-header bg-primary text-white">
                                <h3><i class="fas fa-upload me-2"></i>อัปโหลดรูปภาพสินค้า</h3>
                            </div>
                            <div class="card-body">
                                <form action="/upload-images" method="post" enctype="multipart/form-data">
                                    <div class="mb-3">
                                        <label class="form-label">เลือกรูปภาพ (เลือกได้หลายรูป)</label>
                                        <input type="file" name="files" class="form-control" multiple accept="image/*" required>
                                    </div>
                                    <button type="submit" class="btn btn-primary">อัปโหลด</button>
                                    <a href="/admin" class="btn btn-secondary">กลับ</a>
                                </form>
                                {f'<div class="alert alert-success mt-3">✅ อัปโหลดสำเร็จ: {uploaded}</div>' if uploaded else ''}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(content=html, status_code=200)

