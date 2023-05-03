"""adding skills and tags table

Revision ID: 3d63981c2389
Revises: b8c70e939795
Create Date: 2023-05-03 23:00:03.423560

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3d63981c2389'
down_revision = 'b8c70e939795'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tags',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tags_id'), 'tags', ['id'], unique=False)
    op.create_table('skills',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_skills_id'), 'skills', ['id'], unique=False)
    op.create_table('users_tags',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('tag_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('user_id', 'tag_id')
    )
    op.create_table('users_skills',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('skill_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['skill_id'], ['skills.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('user_id', 'skill_id')
    )
    op.add_column('users', sa.Column('yoe', sa.Integer(), nullable=False))
    op.add_column('users', sa.Column('bio', sa.Text(), nullable=False))
    op.add_column('users', sa.Column('phone_number', sa.String(), nullable=False))
    op.add_column('users', sa.Column('is_active', sa.Boolean(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'is_active')
    op.drop_column('users', 'phone_number')
    op.drop_column('users', 'bio')
    op.drop_column('users', 'yoe')
    op.drop_table('users_skills')
    op.drop_table('users_tags')
    op.drop_index(op.f('ix_skills_id'), table_name='skills')
    op.drop_table('skills')
    op.drop_index(op.f('ix_tags_id'), table_name='tags')
    op.drop_table('tags')
    # ### end Alembic commands ###
