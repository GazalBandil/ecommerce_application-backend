from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import JSONResponse
from app.auth import models, schemas
from sqlalchemy.orm import Session
from app.auth.utils import create_access_token, create_tokens, hash_password, verify_password
from app.core.deps import get_db



router = APIRouter(prefix = '/auth' , tags = ["Authentication"])

@router.post("/signup" , status_code = 201)
def create_user(request: schemas.UserCreate , db:Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == request.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered or user already exists")
    
    new_user = models.User(
        name=request.name,
        email=request.email,
        hashed_password=hash_password(request.hashed_password),
        role=request.role

    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": f"User {new_user.name} created successfully as {new_user.role}"}

@router.post("/login" , status_code=200 , response_model=schemas.Token)
def login_user(request: schemas.UserLogin,db:Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == request.email).first()
    if not user or not verify_password(request.hashed_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid  password")
    
    token = create_tokens(user.email, user.hashed_password, models.Roles(user.role))
    # Create a response and set tokens in cookies
    response = JSONResponse(content={"message": "Login successful"})
    response.set_cookie(
        key="access_token",
        value=token["access_token"],
        httponly=True,
        max_age=60 * 30, 
        secure=False,  
        samesite="Lax",
        path="/"
    )

    response.set_cookie(
        key="refresh_token",
        value=token["refresh_token"],
        httponly=True,
        max_age=60 * 60 * 24 * 7,  # 7 days
        secure=False,
        samesite="Lax",
        path="/"
    )

    return token

@router.get("/logout", status_code=200)
def logout_user():
    response = JSONResponse(content={"message": "Logged out successfully"})
    response.delete_cookie("access_token",path="/")
    response.delete_cookie("refresh_token",path="/")
    return response

# @router.get("/test-cookie")
# def test_cookie(response: Response):
#     response.set_cookie(
#         key="test_cookie",
#         value="working",
#         httponly=True,
#         max_age=30,
#         secure=False,
#         samesite="Lax",
#         path="/"
#     )
#     return {"message": "Test cookie set"}


