from passlib.context import CryptContext
from datetime import datetime, timezone, timedelta
from jose import JWTError, jwt
from typing import Optional, Dict, Any
from app.auth.models import Roles
import os

# --- Configuration ---
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "B7F4698891BCE837E13525741839D")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", 30))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("JWT_REFRESH_EXPIRE_DAYS", 7))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- Password Utilities ---
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# --- Token Generation ---
def _create_token(
    email: str,
    password_hash: str,
    role: Roles,
    expires_delta: timedelta,
    token_type: str = "access"
) -> str:
    expire_time = datetime.now(timezone.utc) + expires_delta
    payload = {
        "sub": email,
        "pwd": password_hash[-6:],  # Fingerprint to ensure token ties to current password
        "role": role.value,
        "type": token_type,
        "exp": expire_time
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def create_access_token(email: str, password_hash: str, role: Roles) -> str:
    return _create_token(
        email=email,
        password_hash=password_hash,
        role=role,
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        token_type="access"
    )

def create_refresh_token(email: str, password_hash: str, role: Roles) -> str:
    return _create_token(
        email=email,
        password_hash=password_hash,
        role=role,
        expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        token_type="refresh"
    )

# --- Token Decoding ---
def decode_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None

# --- Combined Token Creator ---
def create_tokens(email: str, password_hash: str, role: Roles) -> Dict[str, str]:
    return {
        "access_token": create_access_token(email, password_hash, role),
        "refresh_token": create_refresh_token(email, password_hash, role),
        "token_type": "bearer"
    }
