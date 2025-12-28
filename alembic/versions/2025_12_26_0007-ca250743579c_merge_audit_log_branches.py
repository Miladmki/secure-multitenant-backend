"""merge audit log branches

Revision ID: ca250743579c
Revises: e596d51fc4cb
Create Date: 2025-12-26 00:07:07.671736

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ca250743579c'
down_revision: Union[str, Sequence[str], None] = 'e596d51fc4cb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
