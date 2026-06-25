import hashlib
import json
import logging
from functools import lru_cache
from typing import Any

from redis import Redis
from redis.exceptions import RedisError

from app.settings import get_settings

logger = logging.getLogger(__name__)


@lru_cache
def get_redis_client() -> Redis | None:
    redis_url = get_settings().redis_url
    if not redis_url:
        return None
    return Redis.from_url(redis_url, decode_responses=True)


def cache_key(prefix: str, payload: dict[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, default=str, separators=(",", ":"))
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return f"aqarix:{prefix}:{digest}"


def cache_get_json(key: str) -> dict[str, Any] | None:
    client = get_redis_client()
    if client is None:
        return None
    try:
        value = client.get(key)
    except RedisError:
        logger.warning("Redis cache read failed", exc_info=True)
        return None
    if not value:
        return None
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        logger.warning("Redis cache value is invalid JSON", extra={"cache_key": key})
        return None


def cache_set_json(key: str, value: dict[str, Any], ttl_seconds: int) -> None:
    client = get_redis_client()
    if client is None:
        return
    try:
        client.set(key, json.dumps(value, default=str), ex=ttl_seconds)
    except RedisError:
        logger.warning("Redis cache write failed", exc_info=True)
