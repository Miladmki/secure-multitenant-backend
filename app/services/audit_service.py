# app/services/audit_service.py

from sqlalchemy.orm import Session
from app.models.audit_log import AuthorizationAuditLog


def log_permission_denied(
    *,
    db: Session,
    user_id: int | None,
    tenant_id: int | None,
    permission: str,
    reason: str,
    endpoint: str | None,
    method: str | None,
    context: dict | None = None,
):
    log = AuthorizationAuditLog(
        user_id=user_id,
        tenant_id=tenant_id,
        permission=permission,
        reason=reason,
        endpoint=endpoint,
        method=method,
        context=context or {},
    )

    db.add(log)
    db.commit()
