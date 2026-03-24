"""
Sentinel Hub OAuth2 authentication + session helpers.

Uses the sentinelhub-py SDK when available; falls back to raw requests
so the service stays operational with or without the SDK installed.
"""

import logging
import time
from typing import Optional

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

# ── Token cache ───────────────────────────────────────────────────────────────
_token_cache: dict = {"access_token": None, "expires_at": 0}

TOKEN_URL = "https://services.sentinel-hub.com/auth/realms/main/protocol/openid-connect/token"
CDSE_TOKEN_URL = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"


async def get_sentinelhub_token(use_cdse: bool = False) -> Optional[str]:
    """
    Retrieve a valid OAuth2 access token for Sentinel Hub.
    Returns None if credentials are not configured (demo / mock mode).
    """
    now = time.time()
    if _token_cache["access_token"] and now < _token_cache["expires_at"] - 30:
        return _token_cache["access_token"]

    client_id = settings.SENTINELHUB_CLIENT_ID
    client_secret = settings.SENTINELHUB_CLIENT_SECRET

    if not client_id or not client_secret:
        logger.warning(
            "Sentinel Hub credentials not configured — running in demo mode. "
            "Set SENTINELHUB_CLIENT_ID and SENTINELHUB_CLIENT_SECRET in .env"
        )
        return None

    url = CDSE_TOKEN_URL if use_cdse else TOKEN_URL
    payload = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
    }

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(url, data=payload)
        resp.raise_for_status()
        data = resp.json()

    _token_cache["access_token"] = data["access_token"]
    _token_cache["expires_at"] = now + data.get("expires_in", 3600)
    return _token_cache["access_token"]


def build_auth_headers(token: Optional[str]) -> dict:
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}
