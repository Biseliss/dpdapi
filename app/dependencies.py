from fastapi import HTTPException, Header, Depends, Request
from sqlalchemy.orm import Session
from datetime import datetime
from .database import SessionLocal
from . import models

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user_id(request: Request, db: Session = Depends(get_db)) -> int:
    token = request.cookies.get("Authorization")
    if not token:
        raise HTTPException(status_code=401, detail="No Authorization cookie found")

    session_obj = db.query(models.UserSession).filter(
        models.UserSession.token == token,
        models.UserSession.expires >= datetime.utcnow()
    ).first()

    if not session_obj:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    return session_obj.user_id
