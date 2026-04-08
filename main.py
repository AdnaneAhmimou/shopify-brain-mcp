"""
Shopify Brain MCP Server
Integrates Shopify, GA4, Ahrefs, Email, and your Shopify Brain vault

Transport modes:
  stdio  (default) — Claude Desktop spawns this process locally
  sse              — Claude Desktop connects over HTTP to a remote VPS

Usage:
  python main.py              # stdio (local dev)
  python main.py --sse        # SSE HTTP server (VPS / production)
"""

import asyncio
import logging
import sys
from pathlib import Path
from dotenv import load_dotenv
from fastmcp import FastMCP
from contextlib import contextmanager

# Resolve project root relative to this file (works regardless of working directory)
PROJECT_ROOT = Path(__file__).parent
LOG_FILE = PROJECT_ROOT / "logs" / "mcp-server.log"
ENV_FILE = PROJECT_ROOT / ".env"

# Load environment variables
load_dotenv(ENV_FILE)

# Import tool registration functions
from integrations.shopify.tools import register_shopify_tools
from integrations.ga4.tools import register_ga4_tools
from integrations.seo.tools import register_seo_tools
from integrations.email.tools import register_email_tools
from config.settings import validate_config, MCP_SERVER_HOST, MCP_SERVER_PORT

# Configure logging
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(stream=open(sys.stderr.fileno(), mode='w', encoding='utf-8', closefd=False)),
    ]
)
logger = logging.getLogger(__name__)

@contextmanager
def app_context():
    """Initialize app context"""
    logger.info("Initializing app context...")
    try:
        if not validate_config():
            logger.error("Configuration validation failed")
            raise RuntimeError("Missing required configuration")
        yield
    finally:
        logger.info("Closing app context...")

def build_server() -> FastMCP:
    server = FastMCP("shopify-brain-mcp")
    logger.info("FastMCP server created")
    logger.info("Registering tools...")
    register_shopify_tools(server)
    register_ga4_tools(server)
    register_seo_tools(server)
    register_email_tools(server)
    logger.info("All tools registered")
    return server

async def main():
    use_sse = "--sse" in sys.argv

    logger.info(f"Starting Shopify Brain MCP Server (transport={'sse' if use_sse else 'stdio'})...")

    with app_context():
        server = build_server()

        if use_sse:
            logger.info(f"Starting SSE server on {MCP_SERVER_HOST}:{MCP_SERVER_PORT}")
            await server.run_sse_async(host=MCP_SERVER_HOST, port=MCP_SERVER_PORT)
        else:
            logger.info("Starting stdio transport (local Claude Desktop mode)...")
            try:
                await server.run_async()
            except KeyboardInterrupt:
                logger.info("Shutting down MCP Server...")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        exit(1)
