from app.core.policies.base import Policy
from app.core.permissions import Permission
from app.core.role_permissions import ROLE_PERMISSIONS
from app.models.user import User
from app.models.tenant import Tenant


class TenantPolicy(Policy):
    def allows(
        self,
        *,
        user: User,
        tenant: Tenant,
        permission: Permission,
    ) -> bool:
        # 🔐 Tenant isolation
        if user.tenant_id != tenant.id:
            return False

        # Aggregate permissions from all roles
        user_permissions = set()
        for role in user.roles:
            user_permissions |= ROLE_PERMISSIONS.get(role.name, set())

        return permission in user_permissions
