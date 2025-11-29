"""Add assigned_meal table for trainer meal assignments

Revision ID: 1b5b9c3a1ab3
Revises: 28648829bd3b
Create Date: 2025-11-29 13:45:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1b5b9c3a1ab3'
down_revision = '28648829bd3b'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'assigned_meal',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('meal_id', sa.Integer(), sa.ForeignKey('trainer_meal.id', ondelete='CASCADE'), nullable=False),
        sa.Column('trainer_id', sa.Integer(), sa.ForeignKey('user.id', ondelete='CASCADE'), nullable=False),
        sa.Column('member_id', sa.Integer(), sa.ForeignKey('user.id', ondelete='CASCADE'), nullable=False),
        sa.Column('assigned_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.UniqueConstraint('meal_id', 'trainer_id', 'member_id', name='uq_assigned_meal_trainer_member'),
    )


def downgrade():
    op.drop_table('assigned_meal')
