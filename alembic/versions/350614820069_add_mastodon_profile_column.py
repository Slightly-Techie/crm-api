"""add mastodon profile column

Revision ID: 350614820069
Revises: 62987cc2e0e4
Create Date: 2022-12-22 10:12:36.278940

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '350614820069'
down_revision = '62987cc2e0e4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('mastodon_profile', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'mastodon_profile')
    # ### end Alembic commands ###