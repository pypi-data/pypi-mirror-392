"""add_model_id_and_visibility_to_teams

Revision ID: 6cd36c2258fc
Revises: cc1c8506b837
Create Date: 2025-11-15 14:53:41.383124

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6cd36c2258fc'
down_revision: Union[str, Sequence[str], None] = 'cc1c8506b837'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Check if visibility column exists before adding
    conn = op.get_bind()
    result = conn.execute(sa.text("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name='teams' AND column_name='visibility'
    """))
    visibility_exists = result.fetchone() is not None

    if not visibility_exists:
        op.add_column('teams', sa.Column('visibility', sa.String(), nullable=False, server_default='private'))

    # Check if model_id column exists before adding
    result = conn.execute(sa.text("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name='teams' AND column_name='model_id'
    """))
    model_id_exists = result.fetchone() is not None

    if not model_id_exists:
        op.add_column('teams', sa.Column('model_id', sa.String(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Check if columns exist before dropping
    conn = op.get_bind()

    result = conn.execute(sa.text("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name='teams' AND column_name='model_id'
    """))
    if result.fetchone() is not None:
        op.drop_column('teams', 'model_id')

    result = conn.execute(sa.text("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name='teams' AND column_name='visibility'
    """))
    if result.fetchone() is not None:
        op.drop_column('teams', 'visibility')
