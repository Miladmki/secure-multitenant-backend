from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.models.audit_log import AuthorizationAuditLog


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
    Centralized authorization audit logger.

    Rules:
    - Must NEVER raise
    - Must NEVER block authorization
    - Must COMMIT (append-only security log)
    """

    try:
        log = AuthorizationAuditLog(
            user_id=user_id,
            tenant_id=tenant_id,
            permission=permission,
            allowed=allowed,
            reason=reason if not allowed else "permission granted",
            endpoint=endpoint,
            method=method,
            context=context or {},
        )

        db.add(log)
        db.commit()

    except SQLAlchemyError:
        db.rollback()
