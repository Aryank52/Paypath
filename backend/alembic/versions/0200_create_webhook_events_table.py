"""create_webhook_events_table

Revision ID: 0200a1b2c3d4
Revises: 0199be8d9868
Create Date: 2026-11-11 05:25:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0200a1b2c3d4'
down_revision: Union[str, None] = '0199be8d9868'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'webhook_events',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('paypal_event_id', sa.String(length=128), nullable=False),
        sa.Column('transmission_id', sa.String(length=128), nullable=True),
        sa.Column('event_type', sa.String(length=128), nullable=False),
        sa.Column('resource_type', sa.String(length=64), nullable=True),
        sa.Column('resource_id', sa.String(length=128), nullable=True),
        sa.Column('transaction_id', sa.String(length=36), nullable=True),
        sa.Column('status', sa.String(length=64), nullable=False),
        sa.Column('received_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('processed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('payload_hash', sa.String(length=64), nullable=True),
        sa.Column('payload', sa.JSON(), nullable=True),
        sa.Column('processing_error', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['transaction_id'], ['transactions.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('paypal_event_id', name='uq_webhook_events_paypal_event_id')
    )
    op.create_index(op.f('ix_webhook_events_event_type'), 'webhook_events', ['event_type'], unique=False)
    op.create_index(op.f('ix_webhook_events_paypal_event_id'), 'webhook_events', ['paypal_event_id'], unique=True)
    op.create_index(op.f('ix_webhook_events_resource_id'), 'webhook_events', ['resource_id'], unique=False)
    op.create_index(op.f('ix_webhook_events_status'), 'webhook_events', ['status'], unique=False)
    op.create_index(op.f('ix_webhook_events_transaction_id'), 'webhook_events', ['transaction_id'], unique=False)
    op.create_index(op.f('ix_webhook_events_transmission_id'), 'webhook_events', ['transmission_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_webhook_events_transmission_id'), table_name='webhook_events')
    op.drop_index(op.f('ix_webhook_events_transaction_id'), table_name='webhook_events')
    op.drop_index(op.f('ix_webhook_events_status'), table_name='webhook_events')
    op.drop_index(op.f('ix_webhook_events_resource_id'), table_name='webhook_events')
    op.drop_index(op.f('ix_webhook_events_paypal_event_id'), table_name='webhook_events')
    op.drop_index(op.f('ix_webhook_events_event_type'), table_name='webhook_events')
    op.drop_table('webhook_events')
