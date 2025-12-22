# ===== app/models/item.py =====
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from app.core.database import Base


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(String, nullable=True)

    tenant_id = Column(
        Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )

    created_at = Column(
        DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False
    )
    updated_at = Column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=text("CURRENT_TIMESTAMP"),
    )

    tenant = relationship("Tenant", back_populates="items")

    __table_args__ = (
        UniqueConstraint("name", "tenant_id", name="uq_item_name_tenant"),
    )

    def __repr__(self) -> str:
        return f"<Item id={self.id} name={self.name} tenant_id={self.tenant_id}>"
