from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv
import urllib.parse

# โหลด environment variables
load_dotenv()

# รับ DATABASE_URL จาก environment
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./mydb.sqlite3")

# แก้ไข URL สำหรับ PostgreSQL (Render)
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# สร้าง engine ตามประเภทฐานข้อมูล
if DATABASE_URL.startswith("sqlite"):
    # สำหรับ SQLite
    db_path = DATABASE_URL.replace("sqlite:///", "")
    db_dir = os.path.dirname(db_path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
        print(f" Created database directory: {db_dir}")
    
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        pool_size=5,
        max_overflow=10,
        echo=False  # เปลี่ยนเป็น True ถ้าต้องการดู SQL logs
    )
else:
    # สำหรับ PostgreSQL (production)
    engine = create_engine(
        DATABASE_URL,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,  # ตรวจสอบ connection ก่อนใช้งาน
        echo=False
    )

# สร้าง session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class สำหรับ models
Base = declarative_base()

def get_db():
    """Dependency สำหรับ FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ฟังก์ชันช่วยตรวจสอบ connection
def check_db_connection():
    """ตรวจสอบว่าฐานข้อมูลเชื่อมต่อได้"""
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f" Database connection failed: {e}")
        return False