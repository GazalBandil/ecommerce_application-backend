from enum import Enum
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator


class Role(str, Enum):
    admin = "admin"
    user = "user"
    
class UserBase(BaseModel):
    name: str
    email: EmailStr # Email validation
    role: Optional[Role] = Role.user  # Default role is 'user'

class UserCreate(UserBase):
    hashed_password:str = Field(..., min_length=6)

    @field_validator('hashed_password')
    def validate_password(cls, v):
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v

class  UserLogin(BaseModel):
    email: EmailStr
    hashed_password:str  # Password is required for user login   

class User(UserBase):
    id: int
    role: str

    class Config:
        orm_mode = True  # Enable ORM mode to work with SQLAlchemy models

class ForgotPassword(BaseModel):
    email: EmailStr  # Email is required for password reset

class ResetPassword(BaseModel):
    token: str
    new_password:str = Field(..., min_length=6)

    @field_validator('new_password')
    def validate_password(cls, v):
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[Role] = None


class ForgotPassword(BaseModel):
    email: EmailStr

class ResetPassword(BaseModel):
    token: str
    new_password: str