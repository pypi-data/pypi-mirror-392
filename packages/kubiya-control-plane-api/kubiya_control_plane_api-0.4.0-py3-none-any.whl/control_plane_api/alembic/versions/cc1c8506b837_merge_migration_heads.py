"""merge_migration_heads

Revision ID: cc1c8506b837
Revises: 31cd69a644ce, efa2dc427da1
Create Date: 2025-11-15 14:53:36.860089

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cc1c8506b837'
down_revision: Union[str, Sequence[str], None] = ('31cd69a644ce', 'efa2dc427da1')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
