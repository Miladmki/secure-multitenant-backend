# app/schemas/user.py
from pydantic import BaseModel, EmailStr
from pydantic import BaseModel, EmailStr
from pydantic.config import ConfigDict


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserPublic(BaseModel):
    id: int
    email: EmailStr
    model_config = ConfigDict(from_attributes=True)
