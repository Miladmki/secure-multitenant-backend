# app/models/user.py
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, TYPE_CHECKING
from app.core.database import Base

if TYPE_CHECKING:
    from app.models.refresh_token import RefreshToken


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    hashed_password: Mapped[str]

    refresh_tokens: Mapped[List["RefreshToken"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
