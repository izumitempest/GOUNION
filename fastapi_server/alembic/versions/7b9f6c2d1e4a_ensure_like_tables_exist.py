"""Ensure like association tables exist

Revision ID: 7b9f6c2d1e4a
Revises: 39ada022374e
Create Date: 2026-05-20 10:28:00.000000

"""
from typing import Sequence, Union

from alembic import op  # pylint: disable=no-member


# revision identifiers, used by Alembic.
revision: str = "7b9f6c2d1e4a"
down_revision: Union[str, Sequence[str], None] = "39ada022374e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Render has environments where legacy tables exist but association tables don't.
    # Use IF NOT EXISTS to make this safe across mixed database states.
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS post_likes (
            user_id VARCHAR REFERENCES users(id),
            post_id INTEGER REFERENCES posts(id)
        )
        """
    )
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS post_dislikes (
            user_id VARCHAR REFERENCES users(id),
            post_id INTEGER REFERENCES posts(id)
        )
        """
    )
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS comment_likes (
            user_id VARCHAR REFERENCES users(id),
            comment_id INTEGER REFERENCES comments(id)
        )
        """
    )


def downgrade() -> None:
    # Intentionally no-op to avoid destructive changes on shared environments.
    pass

