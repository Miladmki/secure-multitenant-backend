from pydantic import BaseModel, EmailStr
from pydantic.config import ConfigDict


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserPublic(BaseModel):
    id: int
    email: EmailStr
    tenant_id: int
    model_config = ConfigDict(from_attributes=True)
