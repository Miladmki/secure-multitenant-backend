from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship, Mapped
from typing import TYPE_CHECKING, List
from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User

# جدول واسط many-to-many
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True),
)


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)  # مثل "admin", "user"
    description = Column(String, nullable=True)

    users: Mapped[List["User"]] = relationship(
        "User", secondary=user_roles, back_populates="roles"
    )


class Permission(Base):  # اختیاری
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(
        String, unique=True, nullable=False
    )  # مثل "read_users", "delete_tenant"
    role_id = Column(Integer, ForeignKey("roles.id"))
