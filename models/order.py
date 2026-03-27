from sqlalchemy import Column, Integer, ForeignKey, DateTime, Float, String
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_no = Column(String(50), nullable=False)
    order_date = Column(DateTime, default=datetime.now)

    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User")

    customer_id = Column(Integer, ForeignKey("customers.id"))  
    customer = relationship("Customer")

    amount_untaxed = Column(Float)
    amount_tax = Column(Float)
    amount_total = Column(Float)
    state = Column(String(50))

    details = relationship("OrderDetail", back_populates="order", lazy="selectin")

    def __repr__(self):
        return self.order_no


class OrderDetail(Base):
    __tablename__ = "order_details"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))  
    product = relationship("Product", lazy="selectin")
    qty = Column(Integer)
    price = Column(Float)
    amount = Column(Float)

    order = relationship("Order", back_populates="details", lazy="selectin")

    def __repr__(self):
        return str(self.product.name)