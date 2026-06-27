"""Add listing unit price features.

Revision ID: 0006_listing_unit_price_features
Revises: 0005_listing_contact_and_floor_signals
Create Date: 2026-06-27
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0006_listing_unit_price_features"
down_revision: str | None = "0005_listing_contact_and_floor_signals"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("parsed_listing_records", sa.Column("price_per_sqm_jod", sa.Numeric(), nullable=True))
    op.add_column("parsed_listing_records", sa.Column("price_per_dunum_jod", sa.Numeric(), nullable=True))
    op.create_index("ix_parsed_listing_records_price_per_sqm", "parsed_listing_records", ["price_per_sqm_jod"])
    op.create_index(
        "ix_parsed_listing_records_price_per_dunum",
        "parsed_listing_records",
        ["price_per_dunum_jod"],
    )


def downgrade() -> None:
    op.drop_index("ix_parsed_listing_records_price_per_dunum", table_name="parsed_listing_records")
    op.drop_index("ix_parsed_listing_records_price_per_sqm", table_name="parsed_listing_records")
    op.drop_column("parsed_listing_records", "price_per_dunum_jod")
    op.drop_column("parsed_listing_records", "price_per_sqm_jod")
