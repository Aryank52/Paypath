"""alter_evidence_file_url_to_text

Revision ID: 0202a3b4c5d6
Revises: 0201e5f6g7h8
Create Date: 2026-11-13 00:05:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '0202a3b4c5d6'
down_revision: Union[str, None] = '0201e5f6g7h8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.alter_column('evidence', 'file_url',
               existing_type=sa.String(length=500),
               type_=sa.Text(),
               existing_nullable=False)

def downgrade() -> None:
    op.alter_column('evidence', 'file_url',
               existing_type=sa.Text(),
               type_=sa.String(length=500),
               existing_nullable=False)
