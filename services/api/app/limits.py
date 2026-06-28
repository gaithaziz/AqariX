import logging
from datetime import datetime, timezone

from fastapi import HTTPException, Request, status
from redis.exceptions import RedisError

from app.cache import get_redis_client

logger = logging.getLogger(__name__)


UTC = timezone.utc


def request_identity(request: Request, user_id: str | None = None) -> str:
    if user_id:
        return user_id
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",", maxsplit=1)[0].strip()
    return request.client.host if request.client else "unknown"


def enforce_limit(scope: str, identity: str, limit: int, seconds: int) -> None:
    count = _increment(f"limit:{scope}:{identity}", seconds)
    if count is not None and count > limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Please slow down.",
        )


def record_usage(scope: str, alert_at: int) -> None:
    today = datetime.now(UTC).date().isoformat()
    count = _increment(f"usage:{scope}:{today}", 86_400)
    if count == alert_at:
        logger.warning("Usage alert threshold reached", extra={"scope": scope, "count": count})


def _increment(key: str, seconds: int) -> int | None:
    client = get_redis_client()
    if client is None:
        return None
    try:
        count = client.incr(f"aqarix:{key}")
        if count == 1:
            client.expire(f"aqarix:{key}", seconds)
        return count
    except RedisError:
        logger.warning("Redis counter failed open", exc_info=True, extra={"counter_key": key})
        return None
