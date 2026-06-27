"""Add listing contact and floor signals.

Revision ID: 0005_listing_contact_and_floor_signals
Revises: 0004_raw_listing_fingerprints
Create Date: 2026-06-27
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0005_listing_contact_and_floor_signals"
down_revision: str | None = "0004_raw_listing_fingerprints"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("parsed_listing_records", sa.Column("floor_number", sa.Integer(), nullable=True))
    op.add_column("parsed_listing_records", sa.Column("building_age_years", sa.Integer(), nullable=True))
    op.add_column(
        "parsed_listing_records",
        sa.Column("has_phone_number", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "parsed_listing_records",
        sa.Column("contact_exposure", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.create_index("ix_parsed_listing_records_contact_exposure", "parsed_listing_records", ["contact_exposure"])


def downgrade() -> None:
    op.drop_index("ix_parsed_listing_records_contact_exposure", table_name="parsed_listing_records")
    op.drop_column("parsed_listing_records", "contact_exposure")
    op.drop_column("parsed_listing_records", "has_phone_number")
    op.drop_column("parsed_listing_records", "building_age_years")
    op.drop_column("parsed_listing_records", "floor_number")
