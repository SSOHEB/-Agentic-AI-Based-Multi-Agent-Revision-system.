"""add scheduling columns to topics and session_topics junction table

Revision ID: f3a1b2c4d5e6
Revises: 410784c8f154
Create Date: 2026-03-13 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f3a1b2c4d5e6'
down_revision: Union[str, Sequence[str], None] = '410784c8f154'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Add scheduling columns to topics table
    op.add_column('topics', sa.Column(
        'current_interval_day', sa.Integer(), nullable=False, server_default='1'
    ))
    op.add_column('topics', sa.Column(
        'next_review_date', sa.DateTime(timezone=True), nullable=True
    ))
    op.add_column('topics', sa.Column(
        'state', sa.String(), nullable=False, server_default='active'
    ))

    # 2. Create session_topics junction table
    op.create_table('session_topics',
        sa.Column('session_id', sa.UUID(), nullable=False),
        sa.Column('topic_id', sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['quiz_sessions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['topic_id'], ['topics.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('session_id', 'topic_id')
    )

    # 3. Make quiz_sessions.topic_id nullable (multi-topic sessions use junction table)
    op.alter_column('quiz_sessions', 'topic_id', existing_type=sa.UUID(), nullable=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column('quiz_sessions', 'topic_id', existing_type=sa.UUID(), nullable=False)
    op.drop_table('session_topics')
    op.drop_column('topics', 'state')
    op.drop_column('topics', 'next_review_date')
    op.drop_column('topics', 'current_interval_day')
