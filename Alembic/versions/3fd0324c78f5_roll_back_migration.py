"""roll back migration

Revision ID: 3fd0324c78f5
Revises: d2bedfd6f55a
Create Date: 2023-10-16 21:57:31.236321

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3fd0324c78f5'
down_revision = 'd2bedfd6f55a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
