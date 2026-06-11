"""Add open_to_projects to users

Revision ID: d4e5f6a7b8c9
Revises: c1d2e3f4a5b6
Create Date: 2026-06-04 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd4e5f6a7b8c9'
down_revision = 'c1d2e3f4a5b6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Distinct from is_active: "open to project work" availability.
    # Default true so existing members stay visible/available on rollout.
    op.add_column(
        'users',
        sa.Column(
            'open_to_projects',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('true'),
        )
    )


def downgrade() -> None:
    op.drop_column('users', 'open_to_projects')
