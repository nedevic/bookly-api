import uuid
from datetime import date, datetime
from typing import List

from pydantic import BaseModel

# from src.auth.schemas import User
from src.reviews import schemas


class Book(BaseModel):
    uid: uuid.UUID
    title: str
    author: str
    publisher: str
    published_date: date
    page_count: int
    language: str
    created_at: datetime
    updated_at: datetime


class BookRelations(Book):
    # user: User
    reviews: List["schemas.Review"]


class BookCreate(BaseModel):
    title: str
    author: str
    publisher: str
    published_date: str
    page_count: int
    language: str


class BookUpdate(BaseModel):
    title: str
    author: str
    publisher: str
    page_count: int
    language: str
