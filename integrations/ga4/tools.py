"""
Google Analytics 4 MCP Tools
Exposes GA4 data as MCP tools
"""

import logging
from typing import Any, Dict
from fastmcp import FastMCP
from .client import ga4_client

logger = logging.getLogger(__name__)

def register_ga4_tools(server: FastMCP):
    """Register all GA4-related tools with the MCP server"""

    @server.tool()
    async def get_traffic_report(days: int = 30) -> Dict[str, Any]:
        """
        Get website traffic metrics from Google Analytics 4.

        Returns: Sessions, users, traffic sources, pageviews
        """
        logger.info(f"Tool called: get_traffic_report (days={days})")
        try:
            data = await ga4_client.get_traffic_report(days=days)
            return {
                "status": "success",
                "data": data,
                "message": f"Retrieved traffic data for last {days} days"
            }
        except Exception as e:
            logger.error(f"Error fetching traffic data: {e}")
            return {
                "status": "error",
                "message": f"Failed to fetch traffic data: {str(e)}"
            }

    @server.tool()
    async def get_conversion_metrics(days: int = 30) -> Dict[str, Any]:
        """
        Get conversion metrics from Google Analytics 4.

        Returns: Conversion rate, conversions, ecommerce data
        """
        logger.info(f"Tool called: get_conversion_metrics (days={days})")
        try:
            data = await ga4_client.get_conversion_metrics(days=days)
            return {
                "status": "success",
                "data": data,
                "message": f"Retrieved conversion metrics for last {days} days"
            }
        except Exception as e:
            logger.error(f"Error fetching conversions: {e}")
            return {
                "status": "error",
                "message": f"Failed to fetch conversion data: {str(e)}"
            }

    @server.tool()
    async def get_user_engagement(days: int = 30) -> Dict[str, Any]:
        """
        Get user engagement metrics from GA4.

        Returns: Bounce rate, session duration, engagement rate
        """
        logger.info(f"Tool called: get_user_engagement (days={days})")
        try:
            data = await ga4_client.get_user_engagement(days=days)
            return {
                "status": "success",
                "data": data,
                "message": f"Retrieved engagement metrics for last {days} days"
            }
        except Exception as e:
            logger.error(f"Error fetching engagement: {e}")
            return {
                "status": "error",
                "message": f"Failed to fetch engagement data: {str(e)}"
            }

    @server.tool()
    async def get_top_pages(limit: int = 10) -> Dict[str, Any]:
        """
        Get your top-performing pages by traffic.

        Returns: Page paths with traffic metrics
        """
        logger.info(f"Tool called: get_top_pages (limit={limit})")
        try:
            data = await ga4_client.get_top_pages(limit=limit)
            return {
                "status": "success",
                "data": data,
                "message": f"Retrieved top {limit} pages"
            }
        except Exception as e:
            logger.error(f"Error fetching top pages: {e}")
            return {
                "status": "error",
                "message": f"Failed to fetch pages: {str(e)}"
            }

    @server.tool()
    async def authenticate_ga4_oauth(auth_code: str) -> Dict[str, Any]:
        """
        Authenticate with Google Analytics 4 using OAuth code.

        Exchange an authorization code for an access token.
        """
        logger.info("Tool called: authenticate_ga4_oauth")
        try:
            success = await ga4_client.authenticate_oauth(auth_code)
            if success:
                return {
                    "status": "success",
                    "message": "Successfully authenticated with GA4"
                }
            else:
                return {
                    "status": "error",
                    "message": "Failed to authenticate with GA4"
                }
        except Exception as e:
            logger.error(f"Error during GA4 authentication: {e}")
            return {
                "status": "error",
                "message": f"Authentication error: {str(e)}"
            }

    logger.info("GA4 tools registered")
