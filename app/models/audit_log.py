# app/models/audit_log.py

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    JSON,
    Index,
)
from sqlalchemy.sql import func
from app.core.database import Base


class AuthorizationAuditLog(Base):
    __tablename__ = "authorization_audit_logs"

    id = Column(Integer, primary_key=True)

    # Actor
    user_id = Column(Integer, nullable=True, index=True)
    tenant_id = Column(Integer, nullable=True, index=True)

    # Authorization decision
    permission = Column(String, nullable=False, index=True)
    allowed = Column(Boolean, nullable=False)

    # Reason for denial (nullable for allowed actions)
    reason = Column(String, nullable=True)

    # Request context
    endpoint = Column(String, nullable=True)
    method = Column(String, nullable=True)

    # Arbitrary structured metadata
    context = Column(JSON, nullable=True)

    # Timestamp
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )


# Optional composite indexes for common queries
Index(
    "ix_auth_audit_user_tenant_time",
    AuthorizationAuditLog.user_id,
    AuthorizationAuditLog.tenant_id,
    AuthorizationAuditLog.created_at,
)
