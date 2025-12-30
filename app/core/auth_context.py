from dataclasses import dataclass


@dataclass
class AuthorizationDecision:
    user_id: int | None
    tenant_id: int | None
    permission: str
    allowed: bool
    reason: str | None = None

    def __str__(self):
        return f"AuthorizationDecision(user_id={self.user_id}, tenant_id={self.tenant_id}, permission={self.permission}, allowed={self.allowed}, reason={self.reason})"
