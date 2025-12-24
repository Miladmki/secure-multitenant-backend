from typing import Iterable

from app.core.permissions import Permission
from app.core.role_permissions import ROLE_PERMISSIONS
from app.core.policies.tenant_policy import TenantIsolationPolicy, SelfAccessPolicy
from app.models.user import User
from app.models.tenant import Tenant


# ------------------------------------------------------------------
# Policy registry: permission → list[policy]
# Order matters (fail-fast)
# ------------------------------------------------------------------

POLICY_REGISTRY = {
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
    Permission.ADMIN_DASHBOARD: [
        TenantIsolationPolicy(),
    ],
}


# ------------------------------------------------------------------
# Errors
# ------------------------------------------------------------------


class AuthorizationError(Exception):
    pass


# ------------------------------------------------------------------
# Permission matching (supports wildcard later)
# ------------------------------------------------------------------


def permission_matches(granted: Permission, required: Permission) -> bool:
    if granted == required:
        return True

    # future-proof: users:* → users:read
    if granted.value.endswith("*"):
        return required.value.startswith(granted.value[:-1])

    return False


# ------------------------------------------------------------------
# Central Authorization Resolver (ENGINE)
# ------------------------------------------------------------------


def resolve_permission(
    *,
    user: User,
    tenant: Tenant,
    permission: str,
    resource_owner_id: int | None = None,
) -> None:
    """
    Central authorization resolver.
    DENY-BY-DEFAULT.
    Raises AuthorizationError if access is denied.
    """

    # 0️⃣ Validate permission
    try:
        required_permission = Permission(permission)
    except ValueError:
        raise AuthorizationError("Unknown permission")

    # 1️⃣ Collect permissions from ALL user roles
    granted_permissions: set[Permission] = set()

    for role in user.roles:
        granted_permissions |= ROLE_PERMISSIONS.get(role.name, set())

    if not granted_permissions:
        raise AuthorizationError("User has no permissions")

    # 2️⃣ Permission check (RBAC layer)
    if not any(permission_matches(p, required_permission) for p in granted_permissions):
        raise AuthorizationError("Permission denied")

    # 3️⃣ Policy enforcement (ABAC / contextual)
    policies = POLICY_REGISTRY.get(required_permission)

    # ❌ deny-by-default if no policy registered
    if not policies:
        raise AuthorizationError("No policy defined for permission")

    for policy in policies:
        allowed = policy.allows(
            user=user,
            tenant=tenant,
            resource_owner_id=resource_owner_id,
        )
        if not allowed:
            raise AuthorizationError("Policy denied access")

    # ✅ allowed implicitly by not raising
