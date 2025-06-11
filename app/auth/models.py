from sqlalchemy import Column, Integer, String
from app.core.database import Base
from sqlalchemy.orm import relationship
import enum


class Roles(enum.Enum):
    admin = "admin"
    user = "user"

class User(Base): # Base class for SQLAlchemy models
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)   
    email = Column(String, unique=True, index=True , nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="user")

    cart_items = relationship("Cart", back_populates="user")