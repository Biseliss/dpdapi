from pydantic import BaseModel, ConfigDict, EmailStr, Field
from datetime import date, datetime
from typing import List, Optional

class UserCreate(BaseModel):
    username: str = Field(..., max_length=32)
    email: EmailStr
    password: str
    name: Optional[str] = None
    surname: Optional[str] = None


class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    name: Optional[str] = None
    surname: Optional[str] = None
    avatar: Optional[str] = None
    is_admin: bool

    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    username_or_email: str
    password: str


class UserSessionOut(BaseModel):
    sessionToken: str
    expires: datetime

    class Config:
        orm_mode = True


class LoginRequest(BaseModel):
    username_or_email: str
    password: str


class TokenResponse(BaseModel):
    token: str
    expires: datetime


class PostCreate(BaseModel):
    title: str
    text: Optional[str] = None


class PostOut(BaseModel):
    id: int
    title: str
    text: Optional[str]
    created_at: datetime
    preview: Optional[str] = None
    rating: int
    author: UserOut

    class Config:
        orm_mode = True


class PostDetail(BaseModel):
    id: int
    title: str
    text: Optional[str]
    created_at: datetime
    preview: Optional[str]
    author: UserOut
    rating: int

    class Config:
        orm_mode = True


class CommentCreate(BaseModel):
    post_id: int
    text: str


class CommentOut(BaseModel):
    id: int
    user: UserOut
    post_id: int
    text: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaginatedComments(BaseModel):
    total: int
    page: int
    per_page: int
    data: List[CommentOut]


class RatePostRequest(BaseModel):
    post_id: int
    like: bool


class SendCodeRequest(BaseModel):
    reason: str


class ConfirmEmailRequest(BaseModel):
    code: str
