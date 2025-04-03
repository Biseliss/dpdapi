from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session, joinedload

from ..database import SessionLocal
from ..dependencies import get_current_user_id
from .. import models, schemas, utils

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/feed", response_model=list[schemas.PostOut])
def get_feed(page: int = 1, db: Session = Depends(get_db)):
    per_page = 10
    skip = (page - 1) * per_page
    posts_query = db.query(models.Post).options(joinedload(models.Post.author))\
                    .order_by(models.Post.created_at.desc())
    total = posts_query.count()
    posts = posts_query.offset(skip).limit(per_page).all()

    for post in posts:
        if post.text:
            post.text = utils.cut_string(post.text, 400)

    return posts

@router.get("", response_model=schemas.PostDetail)
def get_recipe(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@router.post("/", response_model=schemas.PostOut)
def create_recipe(
    title: str = Form(...),
    text: str = Form(None),
    preview: UploadFile = File(None),  # может отсутствовать
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    preview_filename = None
    if preview is not None:
        allowed_types = ["image/jpeg", "image/png", "image/gif"]
        if preview.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail="Only image files (JPEG, PNG, GIF) are allowed")
        preview_filename = utils.store_file_in_directory(preview, base_dir="uploads")

    new_post = models.Post(
        user_id=user_id,
        title=title,
        text=text or "",
        preview=preview_filename
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post

@router.delete("/")
def delete_recipe(post_id: int,
                  db: Session = Depends(get_db),
                  user_id: int = Depends(get_current_user_id)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    db.delete(post)
    db.commit()
    return {"detail": "Post deleted"}

@router.post("/rate_post")
def rate_post(data: schemas.RatePostRequest,
              db: Session = Depends(get_db),
              user_id: int = Depends(get_current_user_id)):
    post = db.query(models.Post).filter(models.Post.id == data.post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    existing_like = db.query(models.PostLike).filter(
        models.PostLike.user_id == user_id,
        models.PostLike.post_id == data.post_id
    ).first()

    value = 1 if data.like else -1

    if existing_like:
        existing_like.value = value
    else:
        new_like = models.PostLike(
            user_id=user_id,
            post_id=data.post_id,
            value=value
        )
        db.add(new_like)
    db.commit()
    return {"detail": "Post rated"}
