import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Review(BaseModel):
    uid: uuid.UUID
    rating: int = Field(ge=1, le=5)
    review_text: str
    book_uid: Optional[uuid.UUID]
    user_uid: Optional[uuid.UUID]
    created_at: datetime
    updated_at: datetime


class ReviewCreate(BaseModel):
    rating: int = Field(ge=1, le=5)
    review_text: str
