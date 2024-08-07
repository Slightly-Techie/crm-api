"""project-updates2

Revision ID: 5a735002ced5
Revises: 51a77273c07b
Create Date: 2024-08-03 13:49:15.111676

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '5a735002ced5'
down_revision = '51a77273c07b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    project_status_enum = postgresql.ENUM('COMPLETED', 'IN_PROGRESS', 'ON_HOLD', 'BLOCKED', 'CANCELLED', name='projectstatus', create_type=False)
    project_status_enum.create(op.get_bind(), checkfirst=True)
    op.create_table('project_stacks',
    sa.Column('project_id', sa.Integer(), nullable=False),
    sa.Column('stack_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
    sa.ForeignKeyConstraint(['stack_id'], ['stacks.id'], ),
    sa.PrimaryKeyConstraint('stack_id', 'project_id')
    )
    op.add_column('projects', sa.Column('status', project_status_enum, nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('projects', 'status')
    op.drop_table('project_stacks')
    # ### end Alembic commands ###
