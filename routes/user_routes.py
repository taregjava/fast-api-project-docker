from fastapi import UploadFile, File, Depends
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User
from schemas import UserCreate, UserResponse
from auth import hash_password, verify_password, create_access_token
from datetime import timedelta
from dependencies import get_current_user  # Adjust path as necessary

import shutil
import os
from fastapi import UploadFile
router = APIRouter()

@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    hashed_pw = hash_password(user.password)
    db_user = User(username=user.username, email=user.email, hashed_password=hashed_pw)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/login")
def login(username: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid username or password")
    access_token = create_access_token(data={"sub": user.username}, expires_delta=timedelta(hours=1))
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/reset-password")
def reset_password(email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    reset_token = create_access_token({"sub": user.email}, expires_delta=timedelta(minutes=10))
    send_email(email, "Reset Your Password", f"Use this token to reset: {reset_token}")
    return {"message": "Password reset email sent"}

@router.post("/upload-profile-picture")
def upload_profile_picture(file: UploadFile, user: User = Depends(get_current_user)):
    file_path = save_file(file)
    return {"message": "File uploaded", "path": file_path}

UPLOAD_DIRECTORY = "uploads/"


def save_file(file: UploadFile) -> str:
    # Ensure the uploads directory exists
    if not os.path.exists(UPLOAD_DIRECTORY):
        os.makedirs(UPLOAD_DIRECTORY)
        print(f"Created directory: {UPLOAD_DIRECTORY}")

    file_path = os.path.join(UPLOAD_DIRECTORY, file.filename)
    print(f"Saving file to: {file_path}")

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        print("File saved successfully!")
    except Exception as e:
        print(f"Error saving file: {e}")

    return file_path