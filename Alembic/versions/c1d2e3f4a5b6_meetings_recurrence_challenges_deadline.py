"""Add scheduled_time/recurrence to meetings, deadline to challenges

Revision ID: c1d2e3f4a5b6
Revises: b2c3d4e5f6a7
Create Date: 2026-03-31 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c1d2e3f4a5b6'
down_revision = 'e89564e882b1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'weekly_meetings',
        sa.Column('scheduled_time', sa.TIMESTAMP(timezone=True), nullable=True)
    )
    op.add_column(
        'weekly_meetings',
        sa.Column('recurrence', sa.String(), nullable=True)
    )
    op.add_column(
        'coding_challenges',
        sa.Column('deadline', sa.TIMESTAMP(timezone=True), nullable=True)
    )


def downgrade() -> None:
    op.drop_column('weekly_meetings', 'scheduled_time')
    op.drop_column('weekly_meetings', 'recurrence')
    op.drop_column('coding_challenges', 'deadline')
