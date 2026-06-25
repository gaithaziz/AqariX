import json
from functools import lru_cache
from typing import Annotated
from urllib.request import urlopen

from fastapi import Depends, Header, HTTPException, status
from jose import JWTError, jwt
from pydantic import BaseModel

from app.settings import Settings, get_settings


class CurrentUser(BaseModel):
    id: str
    roles: list[str] = ["buyer"]


@lru_cache
def get_clerk_jwks(jwks_url: str) -> dict[str, object]:
    with urlopen(jwks_url, timeout=5) as response:
        return json.loads(response.read())


def get_current_user(
    authorization: Annotated[str | None, Header()] = None,
    x_demo_user: Annotated[str | None, Header()] = None,
    settings: Settings = Depends(get_settings),
) -> CurrentUser:
    """Resolve the current user.

    Local development may pass `x-demo-user`. When Clerk settings are present,
    bearer tokens are verified against Clerk JWKS.
    """

    if x_demo_user:
        return CurrentUser(id=x_demo_user)
    if not authorization:
        return CurrentUser(id="anonymous-demo-user")

    token = authorization.removeprefix("Bearer ").strip()

    if not settings or not settings.clerk_jwks_url:
        return CurrentUser(id="clerk-demo-user")

    try:
        claims = jwt.decode(
            token,
            get_clerk_jwks(settings.clerk_jwks_url),
            algorithms=["RS256"],
            issuer=settings.clerk_issuer or None,
            options={"verify_aud": False},
        )
    except (JWTError, OSError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Clerk token",
        ) from exc

    subject = claims.get("sub")
    if not isinstance(subject, str):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Clerk token missing subject",
        )

    roles = claims.get("metadata", {}).get("roles", ["buyer"])
    if not isinstance(roles, list):
        roles = ["buyer"]
    return CurrentUser(id=subject, roles=[str(role) for role in roles])
