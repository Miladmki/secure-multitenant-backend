from app.core.permissions import Permission

ROLE_PERMISSIONS = {
    "admin": {
        Permission.USERS_READ,
        Permission.USERS_WRITE,
        Permission.USERS_DELETE,
        Permission.ITEMS_READ,
        Permission.ITEMS_WRITE,
        Permission.TENANT_READ,
        Permission.TENANT_ADMIN,
        Permission.ADMIN_DASHBOARD,
    },
    "user": {
        Permission.USERS_READ,
        Permission.ITEMS_READ,
    },
}
