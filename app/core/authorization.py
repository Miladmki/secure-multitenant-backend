from typing import Iterable, List
from app.core.permissions import Permission
from app.core.role_permissions import ROLE_PERMISSIONS
from app.core.policies.tenant_policy import TenantIsolationPolicy, SelfAccessPolicy
from app.models.user import User
from app.models.tenant import Tenant


# ------------------------------------------------------------------
# Policy registry: permission → list[policy]
# - Empty list = GLOBAL permission (RBAC only)
# - Missing key = MISCONFIGURATION (deny)
# ------------------------------------------------------------------

POLICY_REGISTRY: dict[Permission, list] = {
    Permission.USERS_READ: [
        TenantIsolationPolicy(),
        SelfAccessPolicy(),
    ],
    Permission.USERS_WRITE: [
        TenantIsolationPolicy(),
        SelfAccessPolicy(),
    ],
    Permission.USERS_DELETE: [
        TenantIsolationPolicy(),
    ],
    Permission.ITEMS_READ: [
        TenantIsolationPolicy(),
    ],
    Permission.ITEMS_WRITE: [
        TenantIsolationPolicy(),
    ],
    Permission.TENANT_READ: [
        TenantIsolationPolicy(),
    ],
    Permission.TENANT_ADMIN: [
        TenantIsolationPolicy(),
    ],
    Permission.ADMIN_DASHBOARD: [],  # GLOBAL — no tenant, no ABAC
}

# ------------------------------------------------------------------
# Errors
# ------------------------------------------------------------------

class AuthorizationError(Exception):
    """
    Raised when authorization fails.
    Contains reason + optional context (audit-ready).
    """

    def __init__(self, reason: str, context: dict | None = None):
        self.reason = reason
        self.context = context or {}
        super().__init__(reason)


# ------------------------------------------------------------------
# Permission matching (supports wildcard)
# ------------------------------------------------------------------

def permission_matches(granted: Permission, required: Permission) -> bool:
    """
    Match permissions exactly or via wildcard.
    """
    if granted == required:
        return True
    if granted.value.endswith("*"):
        return required.value.startswith(granted.value[:-1])
    return False


# ------------------------------------------------------------------
# Central Authorization Resolver (ENGINE)
# ------------------------------------------------------------------

def apply_policy_precedence(policies: List) -> List:
    """
    Organize policies based on precedence (priority) and return ordered policies.
    """
    ordered_policies = sorted(
        policies,
        key=lambda policy: isinstance(policy, TenantIsolationPolicy),
        reverse=True,
    )
    return ordered_policies

def resolve_permission(
    *,
    user: User,
    permission: Permission,
    tenant: Tenant | None = None,
    resource_owner_id: int | None = None,
) -> None:
    """
    Central authorization resolver.
    DENY-BY-DEFAULT.
    Flow:
    1. Aggregate permissions from roles (RBAC)
    2. Permission match
    3. Policy enforcement (ABAC)
    """
    # 1️⃣ Aggregate permissions from ALL user roles
    granted_permissions: set[Permission] = set()
    for role in user.roles:
        granted_permissions |= ROLE_PERMISSIONS.get(role.name, set())

    if not granted_permissions:
        raise AuthorizationError(
            reason="user_has_no_permissions",
            context={"user_id": user.id},
        )

    # 2️⃣ RBAC permission check
    if not any(permission_matches(p, permission) for p in granted_permissions):
        raise AuthorizationError(
            reason="permission_denied",
            context={"user_id": user.id, "permission": permission.value},
        )

    # 3️⃣ Policy enforcement (ABAC)
    if permission not in POLICY_REGISTRY:
        raise AuthorizationError(
            reason="permission_not_registered",
            context={"permission": permission.value},
        )

    policies: Iterable = POLICY_REGISTRY[permission]
    policies = apply_policy_precedence(policies)  # Apply precedence order

    if tenant is None:
        raise AuthorizationError(
            reason="tenant_required",
            context={"permission": permission.value},
        )

    for policy in policies:
        allowed = policy.allows(
            user=user, tenant=tenant, resource_owner_id=resource_owner_id
        )

        if not allowed:
            raise AuthorizationError(
                reason="policy_denied",
                context={
                    "policy": policy.__class__.__name__,
                    "user_id": user.id,
                    "tenant_id": tenant.id,
                    "permission": permission.value,
                },
            )

    return None
