"""
Auth Server — One-time Google OAuth setup via browser.
Run this on the VPS alongside the MCP server.
Client visits http://<vps>:5001 and clicks Authorize — done.
Saves tokens to tokens/google_tokens.json for GA4 + Gmail.
"""

import os
import json
from pathlib import Path
from flask import Flask, redirect, request
from google_auth_oauthlib.flow import Flow
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

app = Flask(__name__)
app.secret_key = os.urandom(24)

PROJECT_ROOT = Path(__file__).parent
CREDENTIALS_FILE = PROJECT_ROOT / "google-oauth-credentials.json"
TOKENS_FILE = PROJECT_ROOT / "tokens" / "google_tokens.json"

VPS_HOST = os.getenv("VPS_HOST", "srv1534106.hstgr.cloud")
REDIRECT_URI = f"http://{VPS_HOST}:5001/callback"

SCOPES = [
    "https://www.googleapis.com/auth/analytics.readonly",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/gmail.readonly",
]


def is_authorized() -> bool:
    return TOKENS_FILE.exists()


@app.route("/")
def index():
    status = "connected" if is_authorized() else "not connected"
    color = "green" if is_authorized() else "orange"
    button = "" if is_authorized() else '<p><a href="/authorize" style="background:#4285f4;color:white;padding:12px 24px;text-decoration:none;border-radius:4px;font-size:16px">Connect Google Account</a></p>'
    revoke = '<p><a href="/revoke" style="color:red;font-size:13px">Disconnect / re-authorize</a></p>' if is_authorized() else ""

    return f"""
    <html><body style="font-family:Arial,sans-serif;max-width:500px;margin:80px auto;padding:20px;text-align:center">
    <h2>Shopify Brain — Google Authorization</h2>
    <p>Status: <strong style="color:{color}">{status}</strong></p>
    {button}
    {revoke}
    <hr style="margin-top:40px">
    <p style="color:#999;font-size:12px">This authorizes GA4 (Analytics) + Gmail access for the MCP server.</p>
    </body></html>
    """


@app.route("/authorize")
def authorize():
    if not CREDENTIALS_FILE.exists():
        return "<h2>Error</h2><p>google-oauth-credentials.json not found on server.</p>", 500

    flow = Flow.from_client_secrets_file(
        str(CREDENTIALS_FILE),
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI,
    )
    auth_url, _ = flow.authorization_url(
        prompt="consent",
        access_type="offline",
    )
    return redirect(auth_url)


@app.route("/callback")
def callback():
    error = request.args.get("error")
    if error:
        return f"<h2>Error: {error}</h2><p><a href='/'>Try again</a></p>"

    if not CREDENTIALS_FILE.exists():
        return "<h2>Error</h2><p>credentials file missing</p>", 500

    flow = Flow.from_client_secrets_file(
        str(CREDENTIALS_FILE),
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI,
    )
    flow.fetch_token(code=request.args.get("code"))
    creds = flow.credentials

    TOKENS_FILE.parent.mkdir(parents=True, exist_ok=True)
    token_data = {
        "token": creds.token,
        "refresh_token": creds.refresh_token,
        "token_uri": creds.token_uri,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "scopes": list(creds.scopes) if creds.scopes else SCOPES,
    }
    with open(TOKENS_FILE, "w") as f:
        json.dump(token_data, f, indent=2)

    return """
    <html><body style="font-family:Arial,sans-serif;max-width:500px;margin:80px auto;padding:20px;text-align:center">
    <h2 style="color:green">Connected!</h2>
    <p>Google account authorized successfully.</p>
    <p>GA4 Analytics and Gmail are now active in the MCP server.</p>
    <p><a href="/">Back to status</a></p>
    </body></html>
    """


@app.route("/revoke")
def revoke():
    if TOKENS_FILE.exists():
        TOKENS_FILE.unlink()
    return redirect("/")


@app.route("/status")
def status():
    return {"authorized": is_authorized(), "tokens_file": str(TOKENS_FILE)}


if __name__ == "__main__":
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    print(f"Auth server running at http://{VPS_HOST}:5001")
    print(f"Redirect URI: {REDIRECT_URI}")
    app.run(host="0.0.0.0", port=5001, debug=False)
