import logging

import httpx
from fastapi import HTTPException
from jose import JWTError, jwt

from app.config import settings

logger = logging.getLogger(__name__)

_cached_public_key: str | None = None


async def _get_keycloak_public_key() -> str:
    global _cached_public_key
    if _cached_public_key:
        return _cached_public_key

    url = f"{settings.keycloak_url}/realms/{settings.keycloak_realm}"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        resp.raise_for_status()
        data = resp.json()
        _cached_public_key = data["public_key"]
        return _cached_public_key


async def verify_token(token: str) -> dict:
    try:
        public_key = await _get_keycloak_public_key()
        pem_key = f"-----BEGIN PUBLIC KEY-----\n{public_key}\n-----END PUBLIC KEY-----"

        payload = jwt.decode(
            token,
            pem_key,
            algorithms=["RS256"],
            audience=settings.keycloak_client_id,
            options={"verify_aud": True, "verify_exp": True},
        )
        return payload
    except JWTError as e:
        logger.warning(f"JWT verification failed: {e}")
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    except httpx.HTTPError as e:
        logger.error(f"Failed to fetch Keycloak public key: {e}")
        raise HTTPException(status_code=503, detail="Authentication service unavailable")
