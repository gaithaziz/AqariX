"""Add raw listing fingerprints.

Revision ID: 0004_raw_listing_fingerprints
Revises: 0003_parsed_listing_quality
Create Date: 2026-06-27
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0004_raw_listing_fingerprints"
down_revision: str | None = "0003_parsed_listing_quality"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("raw_listing_posts", sa.Column("raw_text_fingerprint", sa.Text(), nullable=True))
    op.create_index(
        "ix_raw_listing_posts_source_fingerprint",
        "raw_listing_posts",
        ["source", "raw_text_fingerprint"],
    )


def downgrade() -> None:
    op.drop_index("ix_raw_listing_posts_source_fingerprint", table_name="raw_listing_posts")
    op.drop_column("raw_listing_posts", "raw_text_fingerprint")
