import os
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError,jwt
from app.auth.models import Roles, User
# from app.auth.utils import decode_token
from typing import Annotated, List, Union
from sqlalchemy.orm import Session

from app.core.deps import get_db


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")  # or your actual token route

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "B7F4698891BCE837E13525741839D")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception

    return {"id": user.id, "email": user.email, "role": user.role}

def require_role(required_roles: Union[Roles, List[Roles]]):
    # Convert single role to list for uniform handling
    if isinstance(required_roles, Roles):
        required_roles = [required_roles]
    
    def role_checker(user: dict = Depends(get_current_user)):
        user_role = user.get("role")
        if not user_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Missing role information"
            )
        
        try:
            # Convert string role to Enum for comparison
            user_role_enum = Roles(user_role)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid user role"
            )
        
        if user_role_enum not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires roles: {', '.join([r.value for r in required_roles])}"
            )
        return user
    return role_checker

