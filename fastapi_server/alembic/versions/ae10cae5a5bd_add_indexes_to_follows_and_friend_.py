"""add_indexes_to_follows_and_friend_requests

Revision ID: ae10cae5a5bd
Revises: 85afc623d221
Create Date: 2026-05-26 21:51:22.588012

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'ae10cae5a5bd'
down_revision: Union[str, Sequence[str], None] = '85afc623d221'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_index(op.f('ix_follows_follower_id'), 'follows', ['follower_id'], unique=False)
    op.create_index(op.f('ix_follows_following_id'), 'follows', ['following_id'], unique=False)
    op.create_index(op.f('ix_friend_requests_receiver_id'), 'friend_requests', ['receiver_id'], unique=False)
    op.create_index(op.f('ix_friend_requests_sender_id'), 'friend_requests', ['sender_id'], unique=False)
    op.create_index(op.f('ix_friend_requests_status'), 'friend_requests', ['status'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_friend_requests_status'), table_name='friend_requests')
    op.drop_index(op.f('ix_friend_requests_sender_id'), table_name='friend_requests')
    op.drop_index(op.f('ix_friend_requests_receiver_id'), table_name='friend_requests')
    op.drop_index(op.f('ix_follows_following_id'), table_name='follows')
    op.drop_index(op.f('ix_follows_follower_id'), table_name='follows')
