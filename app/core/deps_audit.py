# app/core/deps_audit.py

from sqlalchemy.orm import Session
from fastapi import Depends
from app.db.session import get_db
from app.services.business_audit_logger import AuditLogger


def get_audit_logger(db: Session = Depends(get_db)) -> AuditLogger:
    return AuditLogger(db)
