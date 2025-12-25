# app/models/audit_log.py

from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.sql import func
from app.core.database import Base


class AuthorizationAuditLog(Base):
    __tablename__ = "authorization_audit_logs"

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, nullable=True)
    tenant_id = Column(Integer, nullable=True)

    permission = Column(String, nullable=False)
    reason = Column(String, nullable=False)

    endpoint = Column(String, nullable=True)
    method = Column(String, nullable=True)

    context = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
