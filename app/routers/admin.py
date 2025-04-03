import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import SessionLocal
from ..dependencies import get_current_user_id
from .. import models, schemas

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def check_if_admin(user_id: int, db: Session):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user or not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin privileges required")

@router.get("/users", response_model=List[schemas.UserOut])
def list_users(db: Session = Depends(get_db), admin_id: int = Depends(get_current_user_id)):
    check_if_admin(admin_id, db)
    users = db.query(models.User).all()
    return users

@router.put("/users/{user_id}/toggle_admin", response_model=schemas.UserOut)
def toggle_admin(user_id: int, db: Session = Depends(get_db), admin_id: int = Depends(get_current_user_id)):
    check_if_admin(admin_id, db)
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_admin = not user.is_admin
    db.commit()
    db.refresh(user)
    return user

@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), admin_id: int = Depends(get_current_user_id)):
    check_if_admin(admin_id, db)
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"detail": f"User {user_id} deleted"}

@router.delete("/users/{user_id}/avatar")
def delete_user_avatar(user_id: int, db: Session = Depends(get_db), admin_id: int = Depends(get_current_user_id)):
    check_if_admin(admin_id, db)
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.avatar:
        raise HTTPException(status_code=404, detail="User has no avatar")

    avatar_path = os.path.join("uploads", user.avatar)
    if os.path.exists(avatar_path):
        os.remove(avatar_path)

    user.avatar = None
    db.commit()
    return {"detail": f"Avatar deleted for user {user_id}"}
