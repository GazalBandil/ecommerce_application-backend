from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.auth.models import Roles
from app.auth.utils import decode_token
from typing import List, Union

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/signin")

def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload

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

