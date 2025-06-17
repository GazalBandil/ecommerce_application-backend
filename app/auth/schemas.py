from enum import Enum
import re
from typing import Optional
from pydantic import BaseModel,Field, field_validator

VALID_TLDS = {
    "com","gov","co","in"
}
class Role(str, Enum):
    admin = "admin"
    user = "user"

class UserBase(BaseModel):
    name: str
    email: str # Email validation
    role: Optional[Role] = Role.user  # Default role is 'user'

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        email_regex = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.(\w{2,})$"
        match = re.match(email_regex, v)
        if not match:
            raise ValueError("Invalid email format")
        
        tld = match.group(1).lower()
        if tld not in VALID_TLDS:
            raise ValueError(f"Invalid or unsupported email domain (TLD: .{tld})")
        
        return v.lower()


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
    email: str
    hashed_password:str  # Password is required for user login   

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        email_regex = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.(\w{2,})$"
        match = re.match(email_regex, v)
        if not match:
            raise ValueError("Invalid email format")
        
        tld = match.group(1).lower()
        if tld not in VALID_TLDS:
            raise ValueError(f"Invalid or unsupported email domain (TLD: .{tld})")
        
        return v.lower()


class User(UserBase):
    id: int
    role: str

    class Config:
        orm_mode = True  # Enable ORM mode to work with SQLAlchemy models

class ForgotPassword(BaseModel):
    email: str  # Email is required for password reset

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
    email: str

class ResetPassword(BaseModel):
    token: str
    new_password: str