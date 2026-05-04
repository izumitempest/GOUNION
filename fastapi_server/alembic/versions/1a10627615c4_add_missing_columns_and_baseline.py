"""Add missing columns and baseline

Revision ID: 1a10627615c4
Revises: 
Create Date: 2026-05-04 11:38:38.745583

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1a10627615c4'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add missing columns if they don't exist (Baseline)."""
    # Using raw SQL with IF NOT EXISTS to match the existing startup migration logic
    # while transitioning to Alembic management.
    op.execute("ALTER TABLE posts ADD COLUMN IF NOT EXISTS video VARCHAR")
    op.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS role VARCHAR DEFAULT 'user'")
    op.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE")
    op.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_verified BOOLEAN DEFAULT FALSE")
    op.execute("ALTER TABLE messages ADD COLUMN IF NOT EXISTS image_url VARCHAR")
    op.execute("ALTER TABLE messages ADD COLUMN IF NOT EXISTS video_url VARCHAR")
    op.execute("ALTER TABLE group_members ADD COLUMN IF NOT EXISTS role VARCHAR DEFAULT 'member'")
    op.execute("ALTER TABLE groups ADD COLUMN IF NOT EXISTS cover_image VARCHAR")


def downgrade() -> None:
    """No downgrade for baseline additive migration."""
    pass
