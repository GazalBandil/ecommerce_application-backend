from sqlalchemy.orm import relationship
from sqlalchemy import Column, ForeignKey, Integer
from app.core.database import Base


class Cart (Base):
    __tablename__ = "cart"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)

    user = relationship("User", back_populates = "cart_items")
    product = relationship("Product" , back_populates = "cart_items")
