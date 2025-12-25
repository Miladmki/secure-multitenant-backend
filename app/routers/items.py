from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_tenant, require_permission
from app.core.permissions import Permission
from app.core.utils import get_scoped_resource_or_forbid

from app.models.tenant import Tenant
from app.models.item import Item

router = APIRouter(
    prefix="/tenants",
    tags=["items"],
)


@router.get(
    "/{tenant_id}/items/{item_id}",
    dependencies=[
        Depends(require_permission(Permission.ITEMS_READ))
    ],
)
def read_item(
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
    item_id: int | None = None,
):
    return get_scoped_resource_or_forbid(db, tenant, Item, item_id)


@router.put(
    "/{tenant_id}/items/{item_id}",
    dependencies=[
        Depends(require_permission(Permission.ITEMS_WRITE))
    ],
)
def update_item(
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
    item_id: int | None = None,
    payload: dict | None = None,
):
    item = get_scoped_resource_or_forbid(db, tenant, Item, item_id)
    # update logic here
    return item


@router.delete(
    "/{tenant_id}/items/{item_id}",
    dependencies=[
        Depends(require_permission(Permission.ITEMS_WRITE))
    ],
)
def delete_item(
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
    item_id: int | None = None,
):
    item = get_scoped_resource_or_forbid(db, tenant, Item, item_id)
    db.delete(item)
    db.commit()
    return {"deleted": True}
