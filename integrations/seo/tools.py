"""
SEO MCP Tools
Exposes SEO analysis and optimization as MCP tools
"""

import logging
from typing import Any, Dict
from mcp.server.fastmcp import FastMCP
from .client import seo_client

logger = logging.getLogger(__name__)

def register_seo_tools(server: FastMCP):
    """Register all SEO-related tools with the MCP server"""

    @server.tool()
    async def audit_product_page(product_url: str) -> Dict[str, Any]:
        """
        Audit a product page for SEO optimization opportunities.

        Returns: SEO score, issues found, optimization recommendations
        """
        logger.info(f"Tool called: audit_product_page ({product_url})")
        try:
            data = await seo_client.audit_product_page(product_url, "")
            return {
                "status": "success",
                "data": data,
                "message": f"Audited product page: {product_url}"
            }
        except Exception as e:
            logger.error(f"Error auditing page: {e}", exc_info=True)
            return {
                "status": "error",
                "message": f"Failed to audit page: {type(e).__name__}: {str(e)}"
            }

    @server.tool()
    async def get_keyword_suggestions(keyword: str) -> Dict[str, Any]:
        """
        Get keyword suggestions and search metrics.

        Returns: Related keywords, search volume, difficulty scores
        """
        logger.info(f"Tool called: get_keyword_suggestions ({keyword})")
        try:
            data = await seo_client.get_keyword_suggestions(keyword)
            return {
                "status": "success",
                "data": data,
                "message": f"Retrieved keywords for: {keyword}"
            }
        except Exception as e:
            logger.error(f"Error getting keywords: {e}", exc_info=True)
            return {
                "status": "error",
                "message": f"Failed to get keywords: {type(e).__name__}: {str(e)}"
            }

    @server.tool()
    async def analyze_competitors(keyword: str, limit: int = 5) -> Dict[str, Any]:
        """
        Analyze top competitors for a keyword.

        Returns: Top ranking domains, their strategies, ranking positions
        """
        logger.info(f"Tool called: analyze_competitors ({keyword})")
        try:
            data = await seo_client.analyze_competitors(keyword, limit)
            return {
                "status": "success",
                "data": data,
                "message": f"Analyzed top {limit} competitors for: {keyword}"
            }
        except Exception as e:
            logger.error(f"Error analyzing competitors: {e}", exc_info=True)
            return {
                "status": "error",
                "message": f"Failed to analyze competitors: {type(e).__name__}: {str(e)}"
            }

    @server.tool()
    async def get_seo_recommendations(product_url: str) -> Dict[str, Any]:
        """
        Get specific SEO optimization recommendations for a product page.

        Returns: Priority recommendations with implementation steps
        """
        logger.info(f"Tool called: get_seo_recommendations ({product_url})")
        try:
            data = await seo_client.get_seo_recommendations(product_url)
            return {
                "status": "success",
                "data": data,
                "message": f"Retrieved SEO recommendations for: {product_url}"
            }
        except Exception as e:
            logger.error(f"Error getting recommendations: {e}")
            return {
                "status": "error",
                "message": f"Failed to get recommendations: {str(e)}"
            }

    logger.info("SEO tools registered")
