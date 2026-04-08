"""
Email MCP Tools
Exposes email sending functionality as MCP tools
"""

import logging
from typing import Any, Dict
from mcp.server.fastmcp import FastMCP
from .service import email_service

logger = logging.getLogger(__name__)

def register_email_tools(server: FastMCP):
    """Register all email-related tools with the MCP server"""

    @server.tool()
    async def send_daily_report(recipient: str, include_products: bool = True, include_traffic: bool = True) -> Dict[str, Any]:
        """
        Send a daily performance report via email.

        Returns: Success/failure status
        """
        logger.info(f"Tool called: send_daily_report (to={recipient})")
        try:
            # TODO: Gather report data from all integrations
            report_data = {
                "products": include_products,
                "traffic": include_traffic,
            }
            success = await email_service.send_daily_report(recipient, report_data)
            return {
                "status": "success" if success else "failed",
                "message": f"Daily report sent to {recipient}" if success else "Failed to send report"
            }
        except Exception as e:
            logger.error(f"Error sending report: {e}")
            return {
                "status": "error",
                "message": f"Failed to send report: {str(e)}"
            }

    @server.tool()
    async def send_inventory_alert(recipient: str) -> Dict[str, Any]:
        """
        Send inventory alert for low stock items.

        Returns: Success/failure status
        """
        logger.info(f"Tool called: send_inventory_alert (to={recipient})")
        try:
            # TODO: Get low stock items from Shopify
            low_stock_items = []
            success = await email_service.send_inventory_alert(recipient, low_stock_items)
            return {
                "status": "success" if success else "failed",
                "message": f"Inventory alert sent to {recipient}" if success else "Failed to send alert"
            }
        except Exception as e:
            logger.error(f"Error sending alert: {e}")
            return {
                "status": "error",
                "message": f"Failed to send alert: {str(e)}"
            }

    logger.info("Email tools registered")
