"""create predicted_data table

Revision ID: 9d9b8fe4a7c1
Revises: 54accc16becb
Create Date: 2026-09-15

"""
from alembic import op
import sqlalchemy as sa


revision = '9d9b8fe4a7c1'
down_revision = '54accc16becb'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'predicted_data',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('Src_IP', sa.Text(), nullable=True),
        sa.Column('Src_Port', sa.BigInteger(), nullable=True),
        sa.Column('Dst_IP', sa.Text(), nullable=True),
        sa.Column('Dst_Port', sa.BigInteger(), nullable=True),
        sa.Column('Protocol', sa.BigInteger(), nullable=True),
        sa.Column('Timestamp', sa.Text(), nullable=True),
        sa.Column('prediction', sa.BigInteger(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('predicted_data')
