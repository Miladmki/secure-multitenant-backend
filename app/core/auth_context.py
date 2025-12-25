# app/core/auth_context.py

from dataclasses import dataclass


@dataclass
class AuthorizationDecision:
    user_id: int | None
    tenant_id: int | None
    permission: str
    allowed: bool
    reason: str | None = None
