from urllib import request
from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import JSONResponse
from app.auth import models, schemas
from sqlalchemy.orm import Session
from app.auth.utils import create_tokens, hash_password, verify_password, create_reset_token,verify_reset_token
from app.auth.email import send_email
from app.core.deps import get_db
from app.auth.schemas import ForgotPassword, ResetPassword
from datetime import datetime, timedelta
from app.auth.utils import generate_reset_token




router = APIRouter(prefix = '/auth' , tags = ["Authentication"])

# Signup endpoint
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


# Login endpoint
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


# logout endpoint
@router.get("/logout", status_code=200)
def logout_user():
    response = JSONResponse(content={"message": "Logged out successfully"})
    response.delete_cookie("access_token",path="/")
    response.delete_cookie("refresh_token",path="/")
    return response


# --- Forgot Password ---
@router.post("/forgot-password")
def forgot_password(data: ForgotPassword, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    token = create_reset_token(user.email)
    expiration = datetime.now()+ timedelta(hours=1)

    reset_token = models.PasswordResetToken(
        user_id=user.id,
        token=token,
        expiration_time=expiration.isoformat(),
        used=False
    )

    db.add(reset_token)
    db.commit()

    reset_link = f"http://localhost:3000/reset-password?token={token}"
    send_email(
        to_email=user.email,
        subject="Reset your password",
        body=f"Click here to reset your password: {reset_link}"
    )
    
    print(f"[INFO] Password reset token for {request.email}: {token}")

    return {"message": "Reset link sent to your email"}



@router.post("/reset-password")
async def reset_password(request: ResetPassword, db: Session = Depends(get_db)):
    # Get email from token
    email = verify_reset_token(request.token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    # Find user by decoded email
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Hash and save new password
    user.hashed_password = hash_password(request.new_password)
    db.commit()

    return {"message": "Password has been reset successfully"}