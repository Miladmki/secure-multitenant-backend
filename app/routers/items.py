# ===== app/routers/items.py =====
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_tenant, require_role
from app.core.utils import get_scoped_resource_or_forbid
from app.models.tenant import Tenant
from app.models.user import User
from app.models.item import Item

router = APIRouter(prefix="/tenants", tags=["items"])


@router.get("/{tenant_id}/items/{item_id}")
def read_item(
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("user")),
    item_id: int = None,
):
    return get_scoped_resource_or_forbid(db, tenant, Item, item_id)


@router.put("/{tenant_id}/items/{item_id}")
def update_item(
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("user")),
    item_id: int = None,
    payload: dict = None,
):
    item = get_scoped_resource_or_forbid(db, tenant, Item, item_id)
    return item


@router.delete("/{tenant_id}/items/{item_id}")
def delete_item(
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("user")),
    item_id: int = None,
):
    item = get_scoped_resource_or_forbid(db, tenant, Item, item_id)
    db.delete(item)
    db.commit()
    return {"deleted": True}
