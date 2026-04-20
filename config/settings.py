"""
Configuration settings loaded from .env file
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Shopify Configuration
_store = os.getenv("SHOPIFY_STORE_URL") or os.getenv("SHOPIFY_STORE", "")
SHOPIFY_STORE_URL = _store if "." in _store else f"{_store}.myshopify.com" if _store else ""
SHOPIFY_API_KEY = os.getenv("SHOPIFY_API_KEY") or os.getenv("SHOPIFY_CLIENT_ID", "")
SHOPIFY_CLIENT_SECRET = os.getenv("SHOPIFY_CLIENT_SECRET", "")
SHOPIFY_ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN", "")
SHOPIFY_API_VERSION = os.getenv("SHOPIFY_API_VERSION", "2024-10")

# Google Analytics 4 Configuration (OAuth)
GA4_PROPERTY_ID = os.getenv("GA4_PROPERTY_ID", "")
GA4_OAUTH_CLIENT_ID = os.getenv("GA4_OAUTH_CLIENT_ID", "")
GA4_OAUTH_CLIENT_SECRET = os.getenv("GA4_OAUTH_CLIENT_SECRET", "")
GA4_OAUTH_REDIRECT_URI = os.getenv("GA4_OAUTH_REDIRECT_URI", "")

# Higgsfield Configuration
HIGGSFIELD_API_KEY_ID = os.getenv("HIGGSFIELD_API_KEY_ID", "")
HIGGSFIELD_API_KEY_SECRET = os.getenv("HIGGSFIELD_API_KEY_SECRET", "")

# Simplified Configuration
SIMPLIFIED_API_TOKEN = os.getenv("SIMPLIFIED_API_TOKEN", "")

# Ahrefs Configuration
AHREFS_MCP_KEY = os.getenv("AHREFS_MCP_KEY", "")

# Anthropic Configuration (Claude API)
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# Email Configuration
EMAIL_SERVICE = os.getenv("EMAIL_SERVICE", "gmail")
EMAIL_FROM = os.getenv("EMAIL_FROM", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))

# MCP Server Configuration
MCP_SERVER_PORT = int(os.getenv("MCP_SERVER_PORT", "5000"))
MCP_SERVER_HOST = os.getenv("MCP_SERVER_HOST", "0.0.0.0")

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "./logs/mcp-server.log")

# Vault Configuration
VAULT_PATH = os.getenv("VAULT_PATH", "")

# Create logs directory relative to project root
Path(__file__).parent.parent.joinpath("logs").mkdir(exist_ok=True)

def validate_config():
    """Validate that required config values are set"""
    required_configs = {
        "Shopify": [SHOPIFY_STORE_URL, SHOPIFY_API_KEY, SHOPIFY_CLIENT_SECRET],
    }

    optional_configs = {
        "GA4": [GA4_PROPERTY_ID, GA4_OAUTH_CLIENT_ID, GA4_OAUTH_CLIENT_SECRET],
        "Ahrefs": [AHREFS_MCP_KEY],
        "Email": [EMAIL_FROM, EMAIL_PASSWORD],
    }

    missing_required = {}
    for service, configs in required_configs.items():
        if not all(configs):
            missing_required[service] = configs

    if missing_required:
        print("⚠️  Missing required configuration:")
        for service in missing_required:
            print(f"  - {service}: Check .env file")
        return False

    missing_optional = [s for s, c in optional_configs.items() if not all(c)]
    if missing_optional:
        print(f"[INFO] Optional integrations not configured: {', '.join(missing_optional)}")

    return True
