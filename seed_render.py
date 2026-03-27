import os
from database import SessionLocal
from models.user import User
from models.category import Category
from models.product import Product
from auth.jwt_handler import hash_password

def init_database():
    """สร้างข้อมูลเริ่มต้นสำหรับ Deploy"""
    print("Starting database seeding...")
    db = SessionLocal()
    
    try:
        # สร้าง Categories
        categories = ['นิยาย', 'การ์ตูน', 'คอมพิวเตอร์', 'เกษตร', 'อุปกรณ์สำนักงาน']
        for cat_name in categories:
            cat = db.query(Category).filter(Category.name == cat_name).first()
            if not cat:
                cat = Category(name=cat_name)
                db.add(cat)
                print(f" Created category: {cat_name}")
        
        db.commit()
        
        # สร้าง Admin User
        admin = db.query(User).filter(User.is_superuser == True).first()
        if not admin:
            admin = User(
                username=os.getenv("ADMIN_USERNAME", "admin"),
                email=os.getenv("ADMIN_EMAIL", "admin@shop.com"),
                password=hash_password(os.getenv("ADMIN_PASSWORD", "admin123")),
                full_name="Administrator",
                is_superuser=True,
                is_active=True
            )
            db.add(admin)
            db.commit()
            print(f"  Created admin: {admin.username}")
        
        print(" Database seeding completed!")
        
    except Exception as e:
        print(f" Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_database()