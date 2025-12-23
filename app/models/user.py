from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    DateTime,
    text,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    is_active = Column(Boolean, nullable=False, server_default=text("1"))

    tenant_id = Column(
        Integer,
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    created_at = Column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )

    # -------------------------
    # Relationships
    # -------------------------

    tenant = relationship("Tenant", back_populates="users")

    # ✅ CRITICAL — MUST MATCH Role.users
    roles = relationship(
        "Role",
        secondary="user_roles",
        back_populates="users",
        lazy="selectin",
    )

    refresh_tokens = relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email} tenant_id={self.tenant_id}>"
