from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, func, select
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(32), unique=True, nullable=False, index=True)
    email = Column(String(320), unique=True, nullable=False, index=True)
    password = Column(String(64), nullable=False)
    name = Column(String(16), nullable=True)
    surname = Column(String(16), nullable=True)
    avatar = Column(String(32), nullable=True)
    is_admin = Column(Boolean, default=False, nullable=False)

    posts = relationship("Post", back_populates="author", cascade="all, delete-orphan")

class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(64), nullable=False)
    text = Column(String(8192), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    preview = Column(String(32), nullable=True)

    author = relationship("User", back_populates="posts")
    likes = relationship("PostLike", back_populates="post", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")

    @hybrid_property
    def rating(self):
        return sum(l.value for l in self.likes) if self.likes else 0

    @rating.expression
    def rating(cls):
        return (
            func.coalesce(
                select(func.sum(PostLike.value))
                .where(PostLike.post_id == cls.id)
                .scalar_subquery(), 0
            )
        )

class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    text = Column(String(2048), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
    post = relationship("Post", back_populates="comments")

class PostLike(Base):
    __tablename__ = "post_likes"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    value = Column(Integer, nullable=False)  # +1 -1

    post = relationship("Post", back_populates="likes")

# реализовать в будущем
class TempCode(Base):
    __tablename__ = "temp_codes"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(6), nullable=False)  # 6 символов (могут быть английские буквы и цифры)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    type = Column(String(24), nullable=False)
    expires = Column(DateTime, nullable=False)

class UserSession(Base):
    __tablename__ = "user_sessions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token = Column(String(64), nullable=False, unique=True)
    expires = Column(DateTime, nullable=False)
