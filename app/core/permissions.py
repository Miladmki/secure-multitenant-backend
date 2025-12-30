from enum import Enum


class Permission(str, Enum):
    # Users
    USERS_READ = "users:read"
    USERS_WRITE = "users:write"
    USERS_DELETE = "users:delete"

    # Items
    ITEMS_READ = "items:read"
    ITEMS_WRITE = "items:write"

    # Tenant
    TENANT_READ = "tenant:read"
    TENANT_ADMIN = "tenant:admin"

    # Admin
    ADMIN_DASHBOARD = "admin:dashboard"

    # Permissions with wildcards
    USERS_ALL = "users:*"  # A wildcard permission to cover all user-related actions
    ITEMS_ALL = "items:*"  # A wildcard permission to cover all item-related actions
