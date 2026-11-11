"""add_user_mobile_and_verification

Revision ID: 0201e5f6g7h8
Revises: 0200a1b2c3d4
Create Date: 2026-11-11 06:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0201e5f6g7h8'
down_revision: Union[str, None] = '0200a1b2c3d4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('mobile_number', sa.String(length=32), nullable=True))
    op.add_column('users', sa.Column('preferred_currency', sa.String(length=3), server_default='USD', nullable=False))
    op.add_column('users', sa.Column('email_verified', sa.Boolean(), server_default=sa.text('false'), nullable=False))
    op.add_column('users', sa.Column('email_verification_token', sa.String(length=128), nullable=True))
    op.add_column('users', sa.Column('email_verification_expires', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'email_verification_expires')
    op.drop_column('users', 'email_verification_token')
    op.drop_column('users', 'email_verified')
    op.drop_column('users', 'preferred_currency')
    op.drop_column('users', 'mobile_number')
