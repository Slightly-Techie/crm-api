"""imageurl-on-skills

Revision ID: f13798207320
Revises: 5a735002ced5
Create Date: 2024-08-03 18:19:08.671773

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f13798207320'
down_revision = '5a735002ced5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('skills', sa.Column('image_url', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('skills', 'image_url')
    # ### end Alembic commands ###
