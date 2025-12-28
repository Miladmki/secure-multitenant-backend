"""make authorization audit logs immutable

Revision ID: e596d51fc4cb
Revises: 72aa8ef6d64c
Create Date: 2025-12-25 19:21:19.473846
"""

from typing import Sequence, Union
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e596d51fc4cb"
down_revision: Union[str, Sequence[str], None] = "72aa8ef6d64c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


FUNCTION_NAME = "prevent_authorization_audit_log_modification"
TABLE_NAME = "authorization_audit_logs"


def upgrade() -> None:
    # 1) Create immutable guard function
    op.execute(
        f"""
        CREATE OR REPLACE FUNCTION {FUNCTION_NAME}()
        RETURNS trigger AS $$
        BEGIN
            RAISE EXCEPTION
                'authorization_audit_logs are immutable (append-only security audit log)';
        END;
        $$ LANGUAGE plpgsql;
        """
    )

    # 2) Block UPDATE
    op.execute(
        f"""
        CREATE TRIGGER trg_auth_audit_no_update
        BEFORE UPDATE ON {TABLE_NAME}
        FOR EACH ROW
        EXECUTE FUNCTION {FUNCTION_NAME}();
        """
    )

    # 3) Block DELETE
    op.execute(
        f"""
        CREATE TRIGGER trg_auth_audit_no_delete
        BEFORE DELETE ON {TABLE_NAME}
        FOR EACH ROW
        EXECUTE FUNCTION {FUNCTION_NAME}();
        """
    )


def downgrade() -> None:
    # NOTE:
    # Downgrading audit-log immutability is NOT recommended in production.
    # This exists only for migration completeness.

    op.execute(f"DROP TRIGGER IF EXISTS trg_auth_audit_no_update ON {TABLE_NAME};")
    op.execute(f"DROP TRIGGER IF EXISTS trg_auth_audit_no_delete ON {TABLE_NAME};")
    op.execute(f"DROP FUNCTION IF EXISTS {FUNCTION_NAME};")
