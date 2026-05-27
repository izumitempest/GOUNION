"""add_created_at_indexes

Revision ID: ad4c0e918c26
Revises: ae10cae5a5bd
Create Date: 2026-05-27 12:25:36.642885

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'ad4c0e918c26'
down_revision: Union[str, Sequence[str], None] = 'ae10cae5a5bd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_index(op.f('ix_activity_logs_created_at'), 'activity_logs', ['created_at'], unique=False)
    op.create_index(op.f('ix_comments_created_at'), 'comments', ['created_at'], unique=False)
    op.create_index(op.f('ix_conversations_created_at'), 'conversations', ['created_at'], unique=False)
    op.create_index(op.f('ix_follows_created_at'), 'follows', ['created_at'], unique=False)
    op.create_index(op.f('ix_friend_requests_created_at'), 'friend_requests', ['created_at'], unique=False)
    op.create_index(op.f('ix_group_requests_created_at'), 'group_requests', ['created_at'], unique=False)
    op.create_index(op.f('ix_groups_created_at'), 'groups', ['created_at'], unique=False)
    op.create_index(op.f('ix_messages_created_at'), 'messages', ['created_at'], unique=False)
    op.create_index(op.f('ix_notifications_created_at'), 'notifications', ['created_at'], unique=False)
    op.create_index(op.f('ix_posts_created_at'), 'posts', ['created_at'], unique=False)
    op.create_index(op.f('ix_reports_created_at'), 'reports', ['created_at'], unique=False)
    op.create_index(op.f('ix_search_history_created_at'), 'search_history', ['created_at'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_search_history_created_at'), table_name='search_history')
    op.drop_index(op.f('ix_reports_created_at'), table_name='reports')
    op.drop_index(op.f('ix_posts_created_at'), table_name='posts')
    op.drop_index(op.f('ix_notifications_created_at'), table_name='notifications')
    op.drop_index(op.f('ix_messages_created_at'), table_name='messages')
    op.drop_index(op.f('ix_groups_created_at'), table_name='groups')
    op.drop_index(op.f('ix_group_requests_created_at'), table_name='group_requests')
    op.drop_index(op.f('ix_friend_requests_created_at'), table_name='friend_requests')
    op.drop_index(op.f('ix_follows_created_at'), table_name='follows')
    op.drop_index(op.f('ix_conversations_created_at'), table_name='conversations')
    op.drop_index(op.f('ix_comments_created_at'), table_name='comments')
    op.drop_index(op.f('ix_activity_logs_created_at'), table_name='activity_logs')
