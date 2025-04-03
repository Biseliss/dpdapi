from fastapi import APIRouter, Depends, Form, HTTPException, File, UploadFile
from pydantic import EmailStr
from sqlalchemy.orm import Session
import os

from app import schemas

from ..database import SessionLocal
from ..dependencies import get_current_user_id
from .. import models
from ..utils import store_file_in_directory

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

UPLOAD_DIR = "uploads/avatars"

@router.get("/me", response_model=schemas.UserOut)
def get_current_user(db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/me/edit", response_model=schemas.UserOut)
def edit_current_user(
    username: str = Form(None),
    email: EmailStr | None = Form(None),
    name: str = Form(None),
    surname: str = Form(None),
    avatar: UploadFile = File(None),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if username is not None:
        existing_user = db.query(models.User).filter(
            models.User.username == username,
            models.User.id != user_id
        ).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Username is already taken")
        user.username = username

    if email is not None:
        existing_email = db.query(models.User).filter(
            models.User.email == email,
            models.User.id != user_id
        ).first()
        if existing_email:
            raise HTTPException(status_code=400, detail="Email is already in use")
        user.email = email

    if name is not None:
        user.name = name
    if surname is not None:
        user.surname = surname

    if avatar is not None:
        avatar_filename = store_file_in_directory(avatar, base_dir="uploads")
        if user.avatar:
            old_path = os.path.join("uploads", user.avatar)
            if os.path.exists(old_path):
                os.remove(old_path)
        user.avatar = avatar_filename

    db.commit()
    db.refresh(user)
    return user

@router.post("/avatar")
def upload_avatar(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    filename = store_file_in_directory(file, base_dir="uploads")

    if user.avatar:
        old_path = os.path.join("uploads", user.avatar)
        if os.path.exists(old_path):
            os.remove(old_path)

    user.avatar = filename
    db.commit()
    db.refresh(user)

    return {"detail": "Avatar uploaded", "filename": filename}

@router.delete("/avatar")
def delete_avatar(db: Session = Depends(get_db),
                  user_id: int = Depends(get_current_user_id)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user or not user.avatar:
        raise HTTPException(status_code=404, detail="Avatar not found")

    file_path = os.path.join(UPLOAD_DIR, user.avatar)
    if os.path.exists(file_path):
        os.remove(file_path)
    user.avatar = None
    db.commit()
    return {"detail": "Avatar deleted"}

@router.delete("/")
def delete_user(email: str, password: str,
                db: Session = Depends(get_db),
                user_id: int = Depends(get_current_user_id)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.email != email or not user.password == password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if user.avatar:
        file_path = os.path.join(UPLOAD_DIR, user.avatar)
        if os.path.exists(file_path):
            os.remove(file_path)

    db.delete(user)
    db.commit()
    return {"detail": f"User {user_id} deleted"}

@router.get("/{username}")
def get_profile(username: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "id": user.id,
        "username": user.username,
        "avatar": user.avatar,
        "name": user.name,
        "surname": user.surname,
    }

@router.get("/{username}/feed")
def get_user_feed(username: str, page: int = 1, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    per_page = 10
    skip = (page - 1) * per_page
    posts = db.query(models.Post).filter(models.Post.user_id == user.id)\
                .order_by(models.Post.created_at.desc())\
                .offset(skip).limit(per_page).all()

    result = []
    for p in posts:
        result.append({
            "id": p.id,
            "title": p.title,
            "preview": p.preview,
            "created_at": p.created_at
        })
    return result
