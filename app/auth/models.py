from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from app.core.database import Base
from sqlalchemy.orm import relationship
import enum

class Roles(enum.Enum):
    admin = "admin"
    user = "user"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)   
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="user")
    reset_tokens = relationship("PasswordResetToken", back_populates="user")
    cart_items = relationship("Cart", back_populates="user")

class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String, unique=True, nullable=False)
    expiration_time = Column(String, nullable=False) 
    used = Column(Boolean, default=False)

    user = relationship("User", back_populates="reset_tokens")