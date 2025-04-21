from sqlalchemy import Column, Integer, String, ForeignKey, Date, Float, Text
from sqlalchemy.orm import relationship

from app.db.base import Base

class Customer(Base):
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
    address = Column(String)
    
    # Relationship with orders (one-to-many)
    orders = relationship("Order", back_populates="customer")
    
    def __repr__(self):
        return f"Customer(id={self.id}, name={self.name}, email={self.email})"


class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    order_date = Column(Date)
    total_amount = Column(Float)
    status = Column(String)
    notes = Column(Text, nullable=True)
    
    # Relationship with customer (many-to-one)
    customer = relationship("Customer", back_populates="orders")
    
    def __repr__(self):
        return f"Order(id={self.id}, customer_id={self.customer_id}, total={self.total_amount})"
