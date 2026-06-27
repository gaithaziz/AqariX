"""Add parsed listing quality fields.

Revision ID: 0003_parsed_listing_quality
Revises: 0002_raw_listing_ingestion
Create Date: 2026-06-27
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0003_parsed_listing_quality"
down_revision: str | None = "0002_raw_listing_ingestion"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "parsed_listing_records",
        sa.Column("quality_score", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "parsed_listing_records",
        sa.Column("quality_grade", sa.Text(), nullable=False, server_default="low"),
    )
    op.add_column(
        "parsed_listing_records",
        sa.Column("is_model_ready", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "parsed_listing_records",
        sa.Column("missing_fields", postgresql.ARRAY(sa.Text()), nullable=False, server_default="{}"),
    )
    op.add_column(
        "parsed_listing_records",
        sa.Column("quality_warnings", postgresql.ARRAY(sa.Text()), nullable=False, server_default="{}"),
    )
    op.create_index("ix_parsed_listing_records_model_ready", "parsed_listing_records", ["is_model_ready"])


def downgrade() -> None:
    op.drop_index("ix_parsed_listing_records_model_ready", table_name="parsed_listing_records")
    op.drop_column("parsed_listing_records", "quality_warnings")
    op.drop_column("parsed_listing_records", "missing_fields")
    op.drop_column("parsed_listing_records", "is_model_ready")
    op.drop_column("parsed_listing_records", "quality_grade")
    op.drop_column("parsed_listing_records", "quality_score")
