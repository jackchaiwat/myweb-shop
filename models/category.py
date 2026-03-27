from sqlalchemy import Column, Integer, String
from database import Base


class Category(Base):
    __tablename__ = "category"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)

    def __repr__(self):
        return self.name