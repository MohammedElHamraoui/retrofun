"""rename blog_views timestamp to created_at

Revision ID: 940c1bae483d
Revises: b5021e1a05fb
Create Date: 2026-11-22 21:55:11.727366

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "940c1bae483d"
down_revision: str | Sequence[str] | None = "b5021e1a05fb"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column("blog_views", "timestamp", new_column_name="created_at", schema="retrofun")


def downgrade() -> None:
    op.alter_column("blog_views", "created_at", new_column_name="timestamp", schema="retrofun")
