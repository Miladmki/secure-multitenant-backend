# ===== app/models/refresh_token.py =====
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    text,
    UniqueConstraint,
    Index,
    Boolean,
)
from sqlalchemy.orm import relationship
from app.core.database import Base
from sqlalchemy import Boolean

revoked = Column(Boolean, nullable=False, server_default="false")


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, nullable=False, index=True)

    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    tenant_id = Column(
        Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )

    revoked = Column(Boolean, nullable=False, server_default=text("0"))

    created_at = Column(
        DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False
    )
    expires_at = Column(DateTime, nullable=False)

    user = relationship("User", back_populates="refresh_tokens")

    __table_args__ = (
        UniqueConstraint("token", name="uq_refresh_token_token"),
        Index("ix_refresh_tokens_user_tenant", "user_id", "tenant_id"),
        Index("ix_refresh_tokens_valid", "token", "revoked"),
    )

    def __repr__(self) -> str:
        return f"<RefreshToken id={self.id} user_id={self.user_id} tenant_id={self.tenant_id} revoked={self.revoked}>"
