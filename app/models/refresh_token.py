from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Index,
    Boolean,
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.core.database import Base


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)

    token = Column(String, unique=True, nullable=False, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    tenant_id = Column(
        Integer,
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
    )

    # store datetimes as timezone-aware where possible
    expires_at = Column(DateTime(timezone=True), nullable=False)

    # both a boolean and a timestamp so tests that set `.revoked = True` work
    revoked = Column(Boolean, default=False, nullable=False)
    revoked_at = Column(DateTime(timezone=True), nullable=True)

    replaced_by_token = Column(String, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    user = relationship("User", back_populates="refresh_tokens")
    tenant = relationship("Tenant")

    __table_args__ = (Index("ix_refresh_token_token_tenant", "token", "tenant_id"),)

    # Helper to coerce naive datetimes to UTC-aware for comparisons
    @staticmethod
    def _ensure_aware(dt: datetime) -> datetime:
        if dt is None:
            return dt
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt

    @property
    def is_expired(self) -> bool:
        expires = self._ensure_aware(self.expires_at)
        return datetime.now(timezone.utc) >= expires

    @property
    def is_revoked(self) -> bool:
        return bool(self.revoked) or (self.revoked_at is not None)
