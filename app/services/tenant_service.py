from sqlalchemy.orm import Session
from app.models.tenant import Tenant
from app.models.user import User

class TenantServiceError(Exception):
    pass

def get_dashboard_data(db: Session, tenant: Tenant, user: User) -> dict:
    # Example: minimal payload; extend with stats as needed
    if user.tenant_id != tenant.id:
        raise TenantServiceError("Tenant mismatch")
    user_count = db.query(User).filter(User.tenant_id == tenant.id).count()
    return {"tenant_id": tenant.id, "tenant_name": tenant.name, "user_count": user_count}
