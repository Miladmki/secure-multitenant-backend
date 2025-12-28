# app/models/audit_log.py

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    Text,
    Index,
)
from sqlalchemy.sql import func
from app.core.database import Base


class AuthorizationAuditLog(Base):
    """
    SECURITY-GRADE AUTHORIZATION AUDIT LOG

    Properties:
    - Append-only
    - Hash-chained (ledger-style)
    - HMAC-signed
    - Tamper-evident
    - Audit-grade (NOT business logging)
    """

    __tablename__ = "authorization_audit_logs"

    id = Column(Integer, primary_key=True)

    # === Actor Context ===
    user_id = Column(Integer, nullable=True, index=True)
    tenant_id = Column(Integer, nullable=True, index=True)

    # === Authorization Decision ===
    permission = Column(String(100), nullable=False, index=True)
    allowed = Column(Boolean, nullable=False)
    reason = Column(Text, nullable=True)

    # === Request Context ===
    endpoint = Column(String(255), nullable=True)
    method = Column(String(10), nullable=True)

    # === Canonical Context Payload (serialized, NOT JSON) ===
    context = Column(Text, nullable=True)

    # === Cryptographic Integrity ===
    signature = Column(String(64), nullable=False)
    prev_hash = Column(String(64), nullable=True)
    entry_hash = Column(String(64), nullable=False)

    integrity_ok = Column(Boolean, nullable=False, default=True)

    # === Timestamp ===
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    __table_args__ = (
        Index(
            "ix_auth_audit_user_tenant_time",
            "user_id",
            "tenant_id",
            "created_at",
        ),
        Index(
            "ix_auth_audit_tenant_time",
            "tenant_id",
            "created_at",
        ),
    )
