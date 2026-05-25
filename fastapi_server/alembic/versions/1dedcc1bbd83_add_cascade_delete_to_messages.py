"""add_cascade_delete_to_messages

Revision ID: 1dedcc1bbd83
Revises: 7b9f6c2d1e4a
Create Date: 2026-05-25 14:40:42.305014

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '1dedcc1bbd83'
down_revision: Union[str, Sequence[str], None] = '7b9f6c2d1e4a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Drop existing foreign key constraint and add the one with ON DELETE CASCADE
    op.drop_constraint('messages_conversation_id_fkey', 'messages', type_='foreignkey')
    op.create_foreign_key('messages_conversation_id_fkey', 'messages', 'conversations', ['conversation_id'], ['id'], ondelete='CASCADE')


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('messages_conversation_id_fkey', 'messages', type_='foreignkey')
    op.create_foreign_key('messages_conversation_id_fkey', 'messages', 'conversations', ['conversation_id'], ['id'])

