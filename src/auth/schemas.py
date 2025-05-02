import uuid
from datetime import datetime
from typing import List

from pydantic import BaseModel, Field

from src.books.schemas import Book
from src.reviews.schemas import Review


class User(BaseModel):
    uid: uuid.UUID
    username: str
    email: str
    first_name: str
    last_name: str
    is_verified: bool
    password_hash: str = Field(exclude=True)
    created_at: datetime
    updated_at: datetime


class UserRelations(User):
    books: List[Book]
    reviews: List[Review]


class UserCreate(BaseModel):
    username: str = Field(max_length=16)
    email: str = Field(max_length=32)
    first_name: str = Field(max_length=32)
    last_name: str = Field(max_length=32)
    password: str = Field(min_length=8)


class UserLogin(BaseModel):
    email: str = Field(max_length=32)
    password: str = Field(min_length=8)
