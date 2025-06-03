import uuid
from datetime import datetime
from typing import List

from pydantic import BaseModel


class Tag(BaseModel):
    uid: uuid.UUID
    name: str
    created_at: datetime


class TagCreate(BaseModel):
    name: str


class TagUpdate(TagCreate):
    pass  # this is currently the same as TagCreate; in the future it might be different


class TagAdd(BaseModel):
    tags: List[TagCreate]
