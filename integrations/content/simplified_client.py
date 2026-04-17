"""
Simplified AI Client
Posts and schedules content to social platforms via Simplified API
Base URL: https://api.simplified.com/api/v1
"""

import logging
import httpx
import os
from typing import Optional

logger = logging.getLogger(__name__)

SIMPLIFIED_BASE = "https://api.simplified.com/api/v1"


def _headers() -> dict:
    token = os.getenv("SIMPLIFIED_API_TOKEN", "")
    if not token:
        raise RuntimeError("SIMPLIFIED_API_TOKEN must be set")
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }


async def get_social_accounts(network: Optional[str] = None) -> dict:
    """Fetch connected social media accounts."""
    params = {}
    if network:
        params["network"] = network

    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.get(
            f"{SIMPLIFIED_BASE}/service/social-media/accounts",
            headers=_headers(),
            params=params,
        )
        logger.info(f"get_social_accounts status={r.status_code} body={r.text[:300]}")
        r.raise_for_status()
        return r.json()


async def create_post(
    account_id: str,
    message: str,
    media_urls: list[str],
    action: str = "add_to_queue",
    scheduled_date: Optional[str] = None,
    platform_extras: Optional[dict] = None,
) -> dict:
    """
    Create and publish/schedule a social media post.

    action: "schedule" | "add_to_queue" | "draft"
    scheduled_date: "YYYY-MM-DD HH:MM" (required when action="schedule")
    media_urls: list of image or video URLs (max 10)
    """
    payload: dict = {
        "accounts_ids": [int(account_id)],
        "message": message,
        "action": action,
        "media": media_urls,
    }
    if scheduled_date:
        payload["date"] = scheduled_date
    if platform_extras:
        payload.update(platform_extras)

    async with httpx.AsyncClient(timeout=30) as client:
        logger.info(f"Creating Simplified post payload={payload}")
        r = await client.post(
            f"{SIMPLIFIED_BASE}/service/social-media/create",
            headers=_headers(),
            json=payload,
        )
        logger.info(f"create_post status={r.status_code} body={r.text[:500]}")
        r.raise_for_status()
        return r.json()
