# app/services/audit_service.py

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.models.audit_log import AuthorizationAuditLog
from app.core.audit_signing import (
    compute_signature,
    compute_entry_hash,
)


def _get_previous_entry_hash(db: Session) -> str | None:
    last = (
        db.query(AuthorizationAuditLog)
        .order_by(AuthorizationAuditLog.id.desc())
        .first()
    )
    return last.entry_hash if last else None


def log_authorization_decision(
    *,
    db: Session,
    user_id: int | None,
    tenant_id: int | None,
    permission: str,
    allowed: bool,
    reason: str,
    endpoint: str | None = None,
    method: str | None = None,
    context: dict | None = None,
) -> None:
    """
    Centralized authorization audit logger (SECURITY-GRADE).

    Guarantees:
    - NEVER raises
    - NEVER blocks authorization
    - Append-only
    - HMAC-signed
    - Hash-chained
    """

    integrity_ok = True
    signature = "DEGRADED"
    entry_hash = "DEGRADED"
    prev_hash = None

    payload = {
        "user_id": user_id,
        "tenant_id": tenant_id,
        "permission": permission,
        "allowed": allowed,
        "reason": reason if not allowed else "permission granted",
        "endpoint": endpoint,
        "method": method,
        "context": context or {},
    }

    try:
        prev_hash = _get_previous_entry_hash(db)
        signature = compute_signature(payload)
        entry_hash = compute_entry_hash(
            prev_hash=prev_hash,
            signature=signature,
        )

    except Exception:
        # Cryptographic failure must NOT block authorization
        integrity_ok = False

    try:
        log = AuthorizationAuditLog(
            user_id=user_id,
            tenant_id=tenant_id,
            permission=permission,
            allowed=allowed,
            reason=payload["reason"],
            endpoint=endpoint,
            method=method,
            context=str(payload["context"]),
            signature=signature,
            prev_hash=prev_hash,
            entry_hash=entry_hash,
            integrity_ok=integrity_ok,
        )

        db.add(log)
        db.commit()

    except SQLAlchemyError:
        db.rollback()
