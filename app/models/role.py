from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship, Mapped
from typing import TYPE_CHECKING, List
from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User

# جدول واسط many-to-many بین User و Role
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column(
        "user_id",
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "role_id",
        Integer,
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    # فقط یک بار ایندکس تعریف می‌کنیم (index=True کافی است)
    name = Column(
        String(100), unique=True, nullable=False, index=True
    )  # مثل "admin", "user"

    users: Mapped[List["User"]] = relationship(
        "User",
        secondary=user_roles,
        back_populates="roles",
        cascade="all",
    )
