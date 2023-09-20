"""add_status_column_to_table

Revision ID: 3b6b08fa6c76
Revises: 8ea2339c4916
Create Date: 2023-09-20 00:35:07.475957

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3b6b08fa6c76'
down_revision = '8ea2339c4916'
branch_labels = None
depends_on = None


def upgrade():
    # Add the 'status' column to your table.
    op.add_column('your_table_name', sa.Column('status', sa.String(length=255), nullable=True))

def downgrade():
    # Remove the 'status' column if needed.
    op.drop_column('your_table_name', 'status')

