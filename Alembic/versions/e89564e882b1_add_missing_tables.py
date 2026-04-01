"""Add missing tables (email_templates, weekly_meetings, coding_challenges)

Revision ID: e89564e882b1
Revises: b2c3d4e5f6a7
Create Date: 2026-03-31 16:29:58.728294

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e89564e882b1'
down_revision = 'b2c3d4e5f6a7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### Create email_templates table ###
    op.create_table('email_templates',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('template_name', sa.String(), nullable=True),
    sa.Column('html_content', sa.String(), nullable=True),
    sa.Column('subject', sa.String(), nullable=True),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_email_templates_id'), 'email_templates', ['id'], unique=False)
    op.create_index(op.f('ix_email_templates_template_name'), 'email_templates', ['template_name'], unique=True)

    # ### Create weekly_meetings table ###
    op.create_table('weekly_meetings',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('meeting_url', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_weekly_meetings_id'), 'weekly_meetings', ['id'], unique=False)

    # ### Create coding_challenges table ###
    op.create_table('coding_challenges',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=False),
    sa.Column('challenge_type', sa.Enum('LEETCODE', 'SYSTEM_DESIGN', 'GENERAL', name='challengetype'), nullable=False),
    sa.Column('difficulty', sa.String(), nullable=True),
    sa.Column('challenge_url', sa.String(), nullable=True),
    sa.Column('posted_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_coding_challenges_id'), 'coding_challenges', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### Drop coding_challenges table ###
    op.drop_index(op.f('ix_coding_challenges_id'), table_name='coding_challenges')
    op.drop_table('coding_challenges')
    op.execute('DROP TYPE IF EXISTS challengetype')

    # ### Drop weekly_meetings table ###
    op.drop_index(op.f('ix_weekly_meetings_id'), table_name='weekly_meetings')
    op.drop_table('weekly_meetings')

    # ### Drop email_templates table ###
    op.drop_index(op.f('ix_email_templates_template_name'), table_name='email_templates')
    op.drop_index(op.f('ix_email_templates_id'), table_name='email_templates')
    op.drop_table('email_templates')
    # ### end Alembic commands ###
