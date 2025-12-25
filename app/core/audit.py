# app/core/audit.py

from sqlalchemy.orm import Session
from app.services.audit_service import log_permission_denied


def audit_permission_denied(
    *,
    db: Session,
    user,
    tenant,
    permission: str,
    request,
    reason: str,
    context: dict | None = None,
):
    log_permission_denied(
        db=db,
        user_id=getattr(user, "id", None),
        tenant_id=getattr(tenant, "id", None),
        permission=permission,
        reason=reason,
        endpoint=request.url.path if request else None,
        method=request.method if request else None,
        context=context,
    )
