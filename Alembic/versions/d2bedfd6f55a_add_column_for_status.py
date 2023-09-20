"""Add column for status

Revision ID: d2bedfd6f55a
Revises: 8ea2339c4916
Create Date: 2023-09-20 01:25:12.261136

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd2bedfd6f55a'
down_revision = '8ea2339c4916'
branch_labels = None
depends_on = None


def upgrade():
    # Add the 'status' column to your table.
    op.add_column('users', sa.Column('status', sa.String(length=255), nullable=True))

def downgrade():
    # Remove the 'status' column if needed.
    op.drop_column('users', 'status')
