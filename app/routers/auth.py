from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from datetime import datetime

from app.dependencies import get_current_user_id

from ..database import SessionLocal
from .. import models, schemas, utils

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def issue_token(user: models.User, response: Response, db: Session) -> schemas.UserSessionOut:
    token = utils.generate_token_hex(32)
    expires = utils.get_future_time(10080)  # сессия на 7 дней
    new_session = models.UserSession(
        user_id=user.id,
        token=token,
        expires=expires
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)

    response.set_cookie(
        key="Authorization",
        value=token,
        expires=expires.strftime("%a, %d %b %Y %H:%M:%S GMT"),
        httponly=True,
        samesite="strict",
        secure=False  # HTTPS
    )

    return schemas.UserSessionOut(sessionToken=token, expires=expires)

@router.post("/register", response_model=schemas.UserSessionOut)
def register(
    user_data: schemas.UserCreate,
    response: Response,
    db: Session = Depends(get_db)
):
    existing_user = db.query(models.User).filter(
        (models.User.username == user_data.username) | (models.User.email == user_data.email)
    ).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email is already in use")

    hashed_pwd = utils.hash_password(user_data.password)
    new_user = models.User(
        username=user_data.username,
        email=user_data.email,
        password=hashed_pwd,
        name=user_data.name,
        surname=user_data.surname,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return issue_token(new_user, response, db)

@router.post("/login", response_model=schemas.UserSessionOut)
def login(
    credentials: schemas.UserLogin,
    response: Response,
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(
        (models.User.username == credentials.username_or_email) |
        (models.User.email == credentials.username_or_email)
    ).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not utils.verify_password(credentials.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return issue_token(user, response, db)


@router.post("/logout")
def logout(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
    response: Response = None
):
    db.query(models.UserSession).filter(models.UserSession.user_id == user_id).delete()
    db.commit()

    response.delete_cookie(key="Authorization")
    return {"detail": "Logged out"}

# TODO реализовать проверку почты
@router.post("/send_code")
def send_code(data: schemas.SendCodeRequest, db: Session = Depends(get_db), user_id: int = None):
    if not user_id:
        raise HTTPException(status_code=401, detail="Auth required")

    code = utils.generate_code(6)
    expires = utils.get_future_time(10)
    temp = models.TempCode(
        code=code,
        user_id=user_id,
        type=data.reason,
        expires=expires
    )
    db.add(temp)
    db.commit()
    # TODO разбраться с email.mime и сделать отправку
    print(f"[DEBUG] Code for user {user_id}: {code}")
    return {"detail": "Code sent. Check your email (or logs...)"}


@router.post("/confirm_email")
def confirm_email(data: schemas.ConfirmEmailRequest, db: Session = Depends(get_db), user_id: int = None):
    if not user_id:
        raise HTTPException(status_code=401, detail="Auth required")

    temp_code = db.query(models.TempCode).filter(
        models.TempCode.user_id == user_id,
        models.TempCode.code == data.code,
        models.TempCode.type == "email",
        models.TempCode.expires >= datetime.utcnow()
    ).first()

    if not temp_code:
        raise HTTPException(status_code=400, detail="Invalid or expired code")

    db.delete(temp_code)
    db.commit()

    return {"detail": "Email confirmed successfully"}
