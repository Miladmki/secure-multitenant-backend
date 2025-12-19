"""sync models

Revision ID: e720455e6a9f
Revises: 511653d7793d
Create Date: 2025-12-18 12:43:13.046867

"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e720455e6a9f"
down_revision: Union[str, Sequence[str], None] = "511653d7793d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema with batch mode for SQLite."""

    # حذف جدول permissions
    op.drop_index(op.f("ix_permissions_id"), table_name="permissions")
    op.drop_table("permissions")

    # تغییرات روی refresh_tokens
    with op.batch_alter_table("refresh_tokens", schema=None) as batch_op:
        batch_op.add_column(sa.Column("tenant_id", sa.Integer(), nullable=False))
        batch_op.create_index("ix_refresh_token_tenant_id", ["tenant_id"])
        batch_op.create_index("ix_refresh_token_user_id", ["user_id"])
        batch_op.create_unique_constraint("uq_refresh_token_token", ["token"])
        # حذف drop_constraint چون اسم ندارد
        batch_op.create_foreign_key(
            "fk_refresh_tokens_user_id",
            "users",
            ["user_id"],
            ["id"],
            ondelete="CASCADE",
        )
        batch_op.create_foreign_key(
            "fk_refresh_tokens_tenant_id",
            "tenants",
            ["tenant_id"],
            ["id"],
            ondelete="CASCADE",
        )

    # تغییرات روی roles
    with op.batch_alter_table("roles", schema=None) as batch_op:
        batch_op.create_index("ix_roles_name", ["name"], unique=True)
        batch_op.drop_column("description")

    # تغییرات روی user_roles
    with op.batch_alter_table("user_roles", schema=None) as batch_op:
        # حذف drop_constraint چون اسم ندارد
        batch_op.create_foreign_key(
            "fk_user_roles_user_id", "users", ["user_id"], ["id"], ondelete="CASCADE"
        )
        batch_op.create_foreign_key(
            "fk_user_roles_role_id", "roles", ["role_id"], ["id"], ondelete="CASCADE"
        )

    # تغییرات روی users
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.add_column(sa.Column("phone", sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column("profile", sa.String(length=255), nullable=True))
        batch_op.drop_index(op.f("ix_users_email"))
        batch_op.create_index("ix_users_tenant_id", ["tenant_id"])
        batch_op.create_unique_constraint(
            "uq_users_email_tenant", ["email", "tenant_id"]
        )
        # حذف drop_constraint چون اسم ندارد
        batch_op.create_foreign_key(
            "fk_users_tenant_id", "tenants", ["tenant_id"], ["id"], ondelete="CASCADE"
        )


def downgrade() -> None:
    """Downgrade schema with batch mode for SQLite."""

    # تغییرات روی users
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.drop_constraint("fk_users_tenant_id", type_="foreignkey")
        batch_op.drop_constraint("uq_users_email_tenant", type_="unique")
        batch_op.drop_index("ix_users_tenant_id")
        batch_op.create_index(op.f("ix_users_email"), ["email"], unique=True)
        batch_op.drop_column("profile")
        batch_op.drop_column("phone")

    # تغییرات روی user_roles
    with op.batch_alter_table("user_roles", schema=None) as batch_op:
        batch_op.drop_constraint("fk_user_roles_role_id", type_="foreignkey")
        batch_op.drop_constraint("fk_user_roles_user_id", type_="foreignkey")

    # تغییرات روی roles
    with op.batch_alter_table("roles", schema=None) as batch_op:
        batch_op.add_column(sa.Column("description", sa.VARCHAR(), nullable=True))
        batch_op.drop_index("ix_roles_name")

    # تغییرات روی refresh_tokens
    with op.batch_alter_table("refresh_tokens", schema=None) as batch_op:
        batch_op.drop_constraint("fk_refresh_tokens_user_id", type_="foreignkey")
        batch_op.drop_constraint("fk_refresh_tokens_tenant_id", type_="foreignkey")
        batch_op.drop_constraint("uq_refresh_token_token", type_="unique")
        batch_op.drop_index("ix_refresh_token_user_id")
        batch_op.drop_index("ix_refresh_token_tenant_id")
        batch_op.drop_column("tenant_id")

    # بازگرداندن جدول permissions
    op.create_table(
        "permissions",
        sa.Column("id", sa.INTEGER(), nullable=False),
        sa.Column("name", sa.VARCHAR(), nullable=False),
        sa.Column("role_id", sa.INTEGER(), nullable=True),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index(op.f("ix_permissions_id"), "permissions", ["id"])



"""

sqlite3 data\secure_backend.db
.tables
.schema users
.schema refresh_tokens

"""