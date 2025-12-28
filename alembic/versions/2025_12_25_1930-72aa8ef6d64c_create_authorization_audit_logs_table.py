"""create authorization audit logs table

Revision ID: 72aa8ef6d64c
Revises: 5d577185ad5f
Create Date: 2025-12-25 19:30:57.595035
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "72aa8ef6d64c"
down_revision: Union[str, Sequence[str], None] = "5d577185ad5f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "authorization_audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        # Actor context
        sa.Column("user_id", sa.Integer(), nullable=True, index=True),
        sa.Column("tenant_id", sa.Integer(), nullable=True, index=True),
        # Authorization decision
        sa.Column("permission", sa.String(100), nullable=False),
        sa.Column("allowed", sa.Boolean(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        # Request context
        sa.Column("endpoint", sa.String(255), nullable=True),
        sa.Column("method", sa.String(10), nullable=True),
        # Canonical payload
        sa.Column("context", sa.Text(), nullable=True),
        # Cryptographic integrity (ledger-style)
        sa.Column("prev_hash", sa.String(64), nullable=True),
        sa.Column("entry_hash", sa.String(64), nullable=False),
        sa.Column("signature", sa.String(64), nullable=False),
        sa.Column(
            "integrity_ok",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
        # Timestamp
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    op.create_index(
        "ix_auth_audit_user_tenant_time",
        "authorization_audit_logs",
        ["user_id", "tenant_id", "created_at"],
    )

    op.create_index(
        "ix_auth_audit_tenant_time",
        "authorization_audit_logs",
        ["tenant_id", "created_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_auth_audit_tenant_time", table_name="authorization_audit_logs")
    op.drop_index(
        "ix_auth_audit_user_tenant_time",
        table_name="authorization_audit_logs",
    )
    op.drop_table("authorization_audit_logs")
