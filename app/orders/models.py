from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy import DateTime
import enum
from sqlalchemy import Column, Float, ForeignKey, Integer,Enum
from app.core.database import Base

class OrderStatus(enum.Enum):
    pending = "pending"
    paid = "paid"
    cancelled = "cancelled"

class Order(Base):

    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    total_amount = Column(Float , nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.pending)  
    created_at = Column(DateTime, default=datetime.now())

    items = relationship("OrderItem", back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    price_at_purchase = Column(Float, nullable=False)
    order = relationship("Order", back_populates="items")
