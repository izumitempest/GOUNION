"""Add seen_posts table

Revision ID: 39ada022374e
Revises: 1a10627615c4
Create Date: 2026-05-04 12:14:30.877692

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '39ada022374e'
down_revision: Union[str, Sequence[str], None] = '1a10627615c4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Only create the seen_posts table
    op.create_table('seen_posts',
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('post_id', sa.Integer(), nullable=False),
        sa.Column('seen_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['post_id'], ['posts.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('user_id', 'post_id')
    )


def downgrade() -> None:
    op.drop_table('seen_posts')
