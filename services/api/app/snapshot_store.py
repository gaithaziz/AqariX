import logging
from uuid import UUID, uuid4, uuid5

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import Connection, Engine

from app.schemas import Listing, OfferingAnalysis, Recommendation
from app.settings import get_settings

logger = logging.getLogger(__name__)
USER_NAMESPACE = UUID("00000000-0000-4000-8000-00000000a001")

metadata = sa.MetaData()

users = sa.Table(
    "users",
    metadata,
    sa.Column("id", sa.Uuid),
    sa.Column("clerk_user_id", sa.Text),
    sa.Column("status", sa.Text),
)
listings = sa.Table(
    "listings",
    metadata,
    sa.Column("id", sa.Uuid),
    sa.Column("title", sa.Text),
    sa.Column("asking_price_jod", sa.Numeric),
    sa.Column("status", sa.Text),
)
offering_analyses = sa.Table(
    "offering_analyses",
    metadata,
    sa.Column("id", sa.Uuid),
    sa.Column("listing_id", sa.Uuid),
    sa.Column("fair_value_jod", sa.Numeric),
    sa.Column("fair_value_confidence", sa.Text),
    sa.Column("recommendation_label", sa.Text),
    sa.Column("explanation", sa.JSON),
    sa.Column("model_version", sa.Text),
    sa.Column("created_at", sa.DateTime(timezone=True)),
)
recommendation_snapshots = sa.Table(
    "recommendation_snapshots",
    metadata,
    sa.Column("id", sa.Uuid),
    sa.Column("user_id", sa.Uuid),
    sa.Column("listing_id", sa.Uuid),
    sa.Column("rank_position", sa.Integer),
    sa.Column("recommendation_score", sa.Numeric),
    sa.Column("source", sa.Text),
    sa.Column("reason_codes", sa.ARRAY(sa.Text)),
    sa.Column("explanation", sa.Text),
    sa.Column("model_version", sa.Text),
)

_engine: Engine | None = None
_disabled = False


def stable_user_uuid(user_id: str) -> UUID:
    return uuid5(USER_NAMESPACE, user_id)


def load_analysis_snapshot(listing_id: UUID, model_version: str) -> OfferingAnalysis | None:
    engine = _get_engine()
    if engine is None:
        return None
    try:
        with engine.begin() as connection:
            row = connection.execute(
                sa.select(offering_analyses.c.explanation)
                .where(offering_analyses.c.listing_id == listing_id)
                .where(offering_analyses.c.model_version == model_version)
                .order_by(offering_analyses.c.created_at.desc())
                .limit(1)
            ).first()
    except Exception:
        _disable()
        return None
    if not row:
        return None
    try:
        return OfferingAnalysis.model_validate(row.explanation)
    except ValueError:
        logger.warning("Stored offering analysis snapshot is invalid", exc_info=True)
        return None


def save_analysis_snapshot(listing: Listing, analysis: OfferingAnalysis) -> None:
    engine = _get_engine()
    if engine is None:
        return
    try:
        with engine.begin() as connection:
            _upsert_listing(connection, listing)
            connection.execute(
                insert(offering_analyses)
                .values(
                    id=analysis.id,
                    listing_id=analysis.listing_id,
                    fair_value_jod=analysis.fair_value_jod,
                    fair_value_confidence=analysis.fair_value_confidence,
                    recommendation_label=analysis.recommendation_label,
                    explanation=analysis.model_dump(mode="json"),
                    model_version=analysis.model_version,
                )
                .on_conflict_do_nothing(index_elements=["id"])
            )
    except Exception:
        _disable()


def save_recommendation_snapshots(user_id: str, recommendations: list[Recommendation]) -> None:
    engine = _get_engine()
    if engine is None:
        return
    user_uuid = stable_user_uuid(user_id)
    try:
        with engine.begin() as connection:
            _upsert_user(connection, user_uuid, user_id)
            for position, recommendation in enumerate(recommendations, start=1):
                _upsert_listing(connection, recommendation.listing)
                connection.execute(
                    insert(recommendation_snapshots).values(
                        id=uuid4(),
                        user_id=user_uuid,
                        listing_id=recommendation.listing.id,
                        rank_position=position,
                        recommendation_score=recommendation.recommendation_score,
                        source="deterministic_phase1_shell",
                        reason_codes=recommendation.reason_codes,
                        explanation=recommendation.explanation,
                        model_version="deterministic-phase1-shell-v1",
                    )
                )
    except Exception:
        _disable()


def _upsert_user(connection: Connection, user_uuid: UUID, user_id: str) -> None:
    connection.execute(
        insert(users)
        .values(id=user_uuid, clerk_user_id=user_id, status="active")
        .on_conflict_do_nothing(index_elements=["clerk_user_id"])
    )


def _upsert_listing(connection: Connection, listing: Listing) -> None:
    connection.execute(
        insert(listings)
        .values(
            id=listing.id,
            title=listing.title,
            asking_price_jod=listing.asking_price_jod,
            status="active",
        )
        .on_conflict_do_nothing(index_elements=["id"])
    )


def _get_engine() -> Engine | None:
    global _engine
    settings = get_settings()
    if _disabled or not settings.snapshot_persistence_enabled or settings.app_env == "local":
        return None
    if _engine is None:
        _engine = sa.create_engine(settings.database_url, pool_pre_ping=True)
    return _engine


def _disable() -> None:
    global _disabled
    _disabled = True
    logger.warning("PostgreSQL snapshot persistence failed open", exc_info=True)
