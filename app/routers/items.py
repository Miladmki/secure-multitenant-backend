from fastapi import APIRouter, Depends
from app.core.permissions import Permission
from app.core.deps import get_current_tenant, require_permission
from app.models.tenant import Tenant
from app.models.item import Item
from sqlalchemy.orm import Session
from app.core.database import get_db

router = APIRouter(
    prefix="/tenants",
    tags=["items"],
)


@router.get(
    "/{tenant_id}/items/{item_id}",
    dependencies=[Depends(require_permission(Permission.ITEMS_READ))],
)
def read_item(
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
    item_id: int | None = None,
):
    # Your logic to fetch item
    return {"item_id": item_id}


@router.put(
    "/{tenant_id}/items/{item_id}",
    dependencies=[Depends(require_permission(Permission.ITEMS_WRITE))],
)
def update_item(
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
    item_id: int | None = None,
    payload: dict | None = None,
):
    # Your logic to update item
    return {"item_id": item_id}


@router.delete(
    "/{tenant_id}/items/{item_id}",
    dependencies=[Depends(require_permission(Permission.ITEMS_WRITE))],
)
def delete_item(
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
    item_id: int | None = None,
):
    # Your logic to delete item
    return {"msg": "Item deleted"}
