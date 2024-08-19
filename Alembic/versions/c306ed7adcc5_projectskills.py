"""projectskills

Revision ID: c306ed7adcc5
Revises: f13798207320
Create Date: 2024-08-18 23:00:34.955971

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'c306ed7adcc5'
down_revision = 'f13798207320'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('project_skills',
    sa.Column('project_id', sa.Integer(), nullable=False),
    sa.Column('skill_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
    sa.ForeignKeyConstraint(['skill_id'], ['skills.id'], ),
    sa.PrimaryKeyConstraint('skill_id', 'project_id')
    )
    op.drop_column('projects', 'project_tools')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('projects', sa.Column('project_tools', postgresql.ARRAY(sa.VARCHAR()), autoincrement=False, nullable=True))
    op.drop_table('project_skills')
    # ### end Alembic commands ###