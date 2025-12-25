# app/core/policies/tenant_policy.py

from abc import ABC, abstractmethod


class BasePolicy(ABC):
    """
    Base class for all authorization policies.
    Deny-by-default.
    """

    @abstractmethod
    def allows(
        self,
        *,
        user,
        tenant,
        resource_owner_id: int | None = None,
    ) -> bool:
        return False


class TenantIsolationPolicy(BasePolicy):
    """
    Enforces tenant isolation.
    User must belong to the same tenant.
    """

    def allows(
        self,
        *,
        user,
        tenant,
        resource_owner_id: int | None = None,
    ) -> bool:
        if not user or not tenant:
            return False

        return user.tenant_id == tenant.id


class SelfAccessPolicy(BasePolicy):
    """
    Allows access only to own resources.
    Example: user can update/read only themselves.
    """

    def allows(
        self,
        *,
        user,
        tenant,
        resource_owner_id: int | None = None,
    ) -> bool:
        if resource_owner_id is None:
            return False

        return user.id == resource_owner_id
