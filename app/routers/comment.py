from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from datetime import datetime

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

@router.get("", response_model=schemas.PaginatedComments)
def get_comments(post: int, page: int = 1, db: Session = Depends(get_db)):
    per_page = 10
    skip = (page - 1) * per_page

    comments_query = db.query(models.Comment).options(joinedload(models.Comment.user)) \
        .filter(models.Comment.post_id == post)
    total = comments_query.count()
    comments = comments_query.order_by(models.Comment.created_at.desc()) \
                             .offset(skip).limit(per_page).all()

    comment_out_list = [schemas.CommentOut.from_orm(c) for c in comments]

    paginated = schemas.PaginatedComments(
        total=total,
        page=page,
        per_page=per_page,
        data=comment_out_list
    )
    return paginated.model_dump()

@router.post("", response_model=schemas.CommentOut)
def create_comment(data: schemas.CommentCreate,
                   db: Session = Depends(get_db),
                   user_id: int = Depends(get_current_user_id)):
    post = db.query(models.Post).filter(models.Post.id == data.post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    new_comment = models.Comment(
        user_id=user_id,
        post_id=data.post_id,
        text=data.text
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment

@router.delete("")
def delete_comment(comment_id: int,
                   db: Session = Depends(get_db),
                   user_id: int = Depends(get_current_user_id)):
    cmt = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if not cmt:
        raise HTTPException(status_code=404, detail="Comment not found")
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if cmt.user_id != user_id and not user.is_admin:
        raise HTTPException(status_code=403, detail="Access denied")

    db.delete(cmt)
    db.commit()
    return {"detail": "Comment deleted"}
