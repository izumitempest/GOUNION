"""make_messages_sender_id_nullable_set_null

Revision ID: 85afc623d221
Revises: 1dedcc1bbd83
Create Date: 2026-05-26 12:22:44.652352

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '85afc623d221'
down_revision: Union[str, Sequence[str], None] = '1dedcc1bbd83'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint('messages_sender_id_fkey', 'messages', type_='foreignkey')
    op.create_foreign_key('messages_sender_id_fkey', 'messages', 'users', ['sender_id'], ['id'], ondelete='SET NULL')
    op.alter_column('messages', 'sender_id', existing_type=sa.VARCHAR(), nullable=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('messages_sender_id_fkey', 'messages', type_='foreignkey')
    op.create_foreign_key('messages_sender_id_fkey', 'messages', 'users', ['sender_id'], ['id'])
    op.alter_column('messages', 'sender_id', existing_type=sa.VARCHAR(), nullable=False)
