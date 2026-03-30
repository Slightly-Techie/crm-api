"""Add manager_id (org-chart hierarchy) to users

Revision ID: a1b2c3d4e5f6
Revises: c306ed7adcc5
Create Date: 2026-03-20 09:50:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = 'c306ed7adcc5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add nullable manager_id that self-references users.id
    op.add_column(
        'users',
        sa.Column('manager_id', sa.Integer(), nullable=True)
    )
    op.create_foreign_key(
        'fk_users_manager_id_users',  # explicit constraint name
        'users',                       # source table
        'users',                       # referent table (self-reference)
        ['manager_id'],                # local columns
        ['id'],                        # remote columns
        ondelete='SET NULL',           # if a manager is deleted, subordinates keep their row
    )


def downgrade() -> None:
    op.drop_constraint('fk_users_manager_id_users', 'users', type_='foreignkey')
    op.drop_column('users', 'manager_id')
