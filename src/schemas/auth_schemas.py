import uuid
from datetime import datetime

from pydantic import BaseModel, Field


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


class UserCreate(BaseModel):
    username: str = Field(max_length=16)
    email: str = Field(max_length=32)
    first_name: str = Field(max_length=32)
    last_name: str = Field(max_length=32)
    password: str = Field(min_length=8)


class UserLogin(BaseModel):
    email: str = Field(max_length=32)
    password: str = Field(min_length=8)
