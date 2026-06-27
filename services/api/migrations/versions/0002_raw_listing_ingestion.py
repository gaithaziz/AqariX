"""Add raw listing ingestion tables.

Revision ID: 0002_raw_listing_ingestion
Revises: 0001_initial_schema
Create Date: 2026-06-27
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002_raw_listing_ingestion"
down_revision: str | None = "0001_initial_schema"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "raw_listing_posts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("source", sa.Text(), nullable=False),
        sa.Column("external_id", sa.Text(), nullable=True),
        sa.Column("raw_text", sa.Text(), nullable=False),
        sa.Column("source_url", sa.Text(), nullable=True),
        sa.Column("captured_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("source", "external_id", name="uq_raw_listing_posts_source_external_id"),
    )
    op.create_index("ix_raw_listing_posts_source", "raw_listing_posts", ["source"])
    op.create_index("ix_raw_listing_posts_captured_at", "raw_listing_posts", ["captured_at"])

    op.create_table(
        "parsed_listing_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "raw_listing_post_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("raw_listing_posts.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("parser_version", sa.Text(), nullable=False),
        sa.Column("city", sa.Text(), nullable=True),
        sa.Column("intent", sa.Text(), nullable=False),
        sa.Column("property_type", sa.Text(), nullable=True),
        sa.Column("price_jod", sa.Numeric(), nullable=True),
        sa.Column("price_period", sa.Text(), nullable=True),
        sa.Column("negotiable", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("area_sqm", sa.Numeric(), nullable=True),
        sa.Column("land_area_dunum", sa.Numeric(), nullable=True),
        sa.Column("bedrooms", sa.Integer(), nullable=True),
        sa.Column("bathrooms", sa.Integer(), nullable=True),
        sa.Column("furnished", sa.Boolean(), nullable=True),
        sa.Column("audiences", postgresql.ARRAY(sa.Text()), nullable=False, server_default="{}"),
        sa.Column("motivated_seller", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("neighborhoods", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("landmarks", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("location_signals", postgresql.ARRAY(sa.Text()), nullable=False, server_default="{}"),
        sa.Column("extracted_terms", postgresql.ARRAY(sa.Text()), nullable=False, server_default="{}"),
        sa.Column("parser_payload", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_parsed_listing_records_intent", "parsed_listing_records", ["intent"])
    op.create_index(
        "ix_parsed_listing_records_city_property_type",
        "parsed_listing_records",
        ["city", "property_type"],
    )


def downgrade() -> None:
    op.drop_index("ix_parsed_listing_records_city_property_type", table_name="parsed_listing_records")
    op.drop_index("ix_parsed_listing_records_intent", table_name="parsed_listing_records")
    op.drop_table("parsed_listing_records")
    op.drop_index("ix_raw_listing_posts_captured_at", table_name="raw_listing_posts")
    op.drop_index("ix_raw_listing_posts_source", table_name="raw_listing_posts")
    op.drop_table("raw_listing_posts")
