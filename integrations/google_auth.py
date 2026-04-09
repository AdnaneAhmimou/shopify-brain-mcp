"""
Shared Google OAuth handler for GA4 and Gmail
Single auth flow covers both services
"""

import json
import logging
import time
from pathlib import Path
from urllib.parse import urlencode
import httpx

logger = logging.getLogger(__name__)

CREDENTIALS_FILE = Path(__file__).parent.parent / "google-oauth-credentials.json"
TOKEN_FILE = Path(__file__).parent.parent / "tokens" / "google_tokens.json"

SCOPES = [
    "https://www.googleapis.com/auth/analytics.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/userinfo.email",
]

REDIRECT_URI = "http://localhost:5000/auth/google/callback"


def _load_credentials():
    with open(CREDENTIALS_FILE) as f:
        data = json.load(f)
    return data.get("web", data)


def get_auth_url() -> str:
    creds = _load_credentials()
    params = {
        "client_id": creds["client_id"],
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": " ".join(SCOPES),
        "access_type": "offline",
        "prompt": "consent",
    }
    return f"{creds['auth_uri']}?{urlencode(params)}"


async def exchange_code(code: str) -> dict:
    creds = _load_credentials()
    async with httpx.AsyncClient() as client:
        response = await client.post(
            creds["token_uri"],
            data={
                "code": code,
                "client_id": creds["client_id"],
                "client_secret": creds["client_secret"],
                "redirect_uri": REDIRECT_URI,
                "grant_type": "authorization_code",
            },
        )
        response.raise_for_status()
        tokens = response.json()
        _save_tokens(tokens)
        return tokens


async def refresh_tokens() -> dict:
    tokens = load_tokens()
    if not (tokens.get("refresh_token") or tokens.get("token_uri")):
        raise RuntimeError("No refresh token saved")
    creds = _load_credentials()
    async with httpx.AsyncClient() as client:
        response = await client.post(
            creds["token_uri"],
            data={
                "client_id": creds["client_id"],
                "client_secret": creds["client_secret"],
                "refresh_token": tokens["refresh_token"],
                "grant_type": "refresh_token",
            },
        )
        response.raise_for_status()
        new_tokens = response.json()
        # Keep refresh_token (not returned on refresh)
        new_tokens.setdefault("refresh_token", tokens["refresh_token"])
        # Normalize: always save under both 'token' and 'access_token' keys
        new_tokens["token"] = new_tokens.get("access_token") or new_tokens.get("token")
        new_tokens["access_token"] = new_tokens["token"]
        # Store expiry timestamp so we can proactively refresh
        new_tokens["expires_at"] = time.time() + new_tokens.get("expires_in", 3600) - 60
        _save_tokens(new_tokens)
        return new_tokens


def load_tokens() -> dict:
    if TOKEN_FILE.exists():
        with open(TOKEN_FILE) as f:
            return json.load(f)
    return {}


def _save_tokens(tokens: dict):
    TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    existing = load_tokens()
    existing.update(tokens)
    with open(TOKEN_FILE, "w") as f:
        json.dump(existing, f)
    logger.info("Google tokens saved")


def is_token_expired() -> bool:
    tokens = load_tokens()
    expires_at = tokens.get("expires_at")
    if not expires_at:
        return False  # no expiry info, assume valid
    return time.time() > expires_at


def get_access_token() -> str | None:
    tokens = load_tokens()
    # auth_server.py saves as "token", older flow saves as "access_token"
    return tokens.get("access_token") or tokens.get("token")


def is_authenticated() -> bool:
    return bool(get_access_token())
