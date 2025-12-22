# ===== app/models/user_roles.py =====
from sqlalchemy import Table, Column, Integer, ForeignKey, Index
from app.core.database import Base

user_roles = Table(
    "user_roles",
    Base.metadata,
    Column(
        "user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    ),
    Column(
        "role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True
    ),
    Index("ix_user_roles_user_role", "user_id", "role_id"),
)
