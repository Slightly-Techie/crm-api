"""Change manager_id FK from SET NULL to RESTRICT

Subordinate reassignment is now handled at the application level
(OrgChartService.delete_user), so the DB should block raw deletes
that bypass the app layer.

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-03-27 12:00:00.000000

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = 'b2c3d4e5f6a7'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint('fk_users_manager_id_users', 'users', type_='foreignkey')
    op.create_foreign_key(
        'fk_users_manager_id_users',
        'users',
        'users',
        ['manager_id'],
        ['id'],
        ondelete='RESTRICT',
    )


def downgrade() -> None:
    op.drop_constraint('fk_users_manager_id_users', 'users', type_='foreignkey')
    op.create_foreign_key(
        'fk_users_manager_id_users',
        'users',
        'users',
        ['manager_id'],
        ['id'],
        ondelete='SET NULL',
    )
