from abc import ABC, abstractmethod
from app.models.user import User
from app.models.tenant import Tenant
from app.core.permissions import Permission


class Policy(ABC):
    """
    Base Policy
    DENY by default
    """

    def allows(
        self,
        *,
        user: User,
        tenant: Tenant,
        permission: Permission,
    ) -> bool:
        return False
