from sqlalchemy import Column, Integer, String
from database import Base


class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    address = Column(String(200), nullable=True)
    tax_id = Column(String(15), nullable=True)
    
    def __repr__(self):
        return self.name