"""Update projects

Revision ID: b64b00ec3606
Revises: d2bedfd6f55a
Create Date: 2023-10-16 16:11:25.724846

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY


# revision identifiers, used by Alembic.
revision = 'b64b00ec3606'
down_revision = 'd2bedfd6f55a'
branch_labels = None
depends_on = None


# Create the 'projects' table
def upgrade():
    op.create_table(
        "projects",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("project_type", sa.String(), nullable=False),
        sa.Column("project_priority", sa.String(), nullable=False),
        sa.Column("project_tools", sa.String()),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("manager_id", sa.Integer(), sa.ForeignKey("users.id")),
        sa.Column('members', sa.ARRAY(sa.String), nullable=True),
        sa.PrimaryKeyConstraint("id")
    )

# ...

# Create the 'projects' table
def downgrade():
    op.drop_table("projects")
