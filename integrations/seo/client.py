"""
Ahrefs API Client
Handles SEO audits, keyword research, and competitor analysis
"""

import logging
from datetime import date
from typing import Any, Dict
from urllib.parse import urlparse
import httpx
from config.settings import AHREFS_MCP_KEY

logger = logging.getLogger(__name__)

class SEOClient:
    """Ahrefs MCP API client"""

    def __init__(self):
        self.api_key = AHREFS_MCP_KEY
        self.base_url = "https://api.ahrefs.com/mcp/mcp"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    async def audit_product_page(self, product_url: str, product_name: str = "") -> Dict[str, Any]:
        """Audit a product page for SEO metrics"""
        logger.info(f"Auditing product page: {product_url}")
        try:
            async with httpx.AsyncClient() as client:
                domain = urlparse(product_url).netloc

                # Get domain metrics
                url = f"{self.base_url}/site-explorer/metrics"
                params = {"target": domain, "mode": "domain", "date": date.today().isoformat()}

                response = await client.get(url, params=params, headers=self.headers)
                if not response.is_success:
                    logger.error(f"Ahrefs audit error {response.status_code}: {response.text}")
                    return {"url": product_url, "domain": domain, "error": f"Ahrefs {response.status_code}: {response.text[:300]}"}

                data = response.json()
                logger.info(f"Ahrefs raw response keys: {list(data.keys())}")

                # Return raw metrics so Claude can interpret actual field names
                metrics = data.get("metrics", data)  # fallback to full response if no "metrics" key
                logger.info(f"Ahrefs metrics keys: {list(metrics.keys()) if isinstance(metrics, dict) else 'not a dict'}")

                dr = metrics.get("domain_rating") or metrics.get("ahrefs_rank") or metrics.get("dr")
                refdoms = metrics.get("refdomains") or metrics.get("referring_domains") or metrics.get("ref_domains")
                backlinks = metrics.get("backlinks") or metrics.get("total_backlinks")
                traffic = metrics.get("org_traffic") or metrics.get("organic_traffic") or metrics.get("organic_traffic_monthly")

                return {
                    "url": product_url,
                    "domain": domain,
                    "domain_rating": dr,
                    "referring_domains": refdoms,
                    "organic_search_traffic": traffic,
                    "backlinks": backlinks,
                    "raw_metrics": metrics,  # include raw so Claude sees all available fields
                }
        except httpx.HTTPError as e:
            logger.error(f"HTTP error auditing page: {e}")
            raise
        except Exception as e:
            logger.error(f"Error auditing page: {e}")
            raise

    async def get_keyword_suggestions(self, keyword: str, search_volume: bool = True) -> Dict[str, Any]:
        """Get keyword suggestions and search metrics"""
        logger.info(f"Getting keyword suggestions for: {keyword}")
        try:
            async with httpx.AsyncClient() as client:
                url = f"{self.base_url}/keywords-explorer/keyword-ideas"
                params = {
                    "keyword": keyword,
                    "country": "us",
                    "select": "keyword,volume,difficulty,clicks,cpc",
                    "limit": 20,
                }

                response = await client.get(url, params=params, headers=self.headers)
                if not response.is_success:
                    logger.error(f"Ahrefs keyword API error {response.status_code}: {response.text}")
                    return {
                        "keyword": keyword,
                        "results_count": 0,
                        "keywords": [],
                        "error": f"Ahrefs API {response.status_code}: {response.text[:300]}"
                    }
                data = response.json()

                keywords = data.get("keywords", [])
                return {
                    "keyword": keyword,
                    "results_count": len(keywords),
                    "keywords": keywords[:20]
                }
        except httpx.HTTPError as e:
            logger.error(f"HTTP error getting keywords: {e}", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"Error getting keywords: {e}", exc_info=True)
            raise

    async def analyze_competitors(self, keyword: str, limit: int = 5) -> Dict[str, Any]:
        """Analyze top competitors for a keyword"""
        logger.info(f"Analyzing competitors for keyword: {keyword}")
        try:
            async with httpx.AsyncClient() as client:
                url = f"{self.base_url}/keywords-explorer/serp-overview"
                params = {
                    "keywords": keyword,
                    "country": "US"
                }

                response = await client.get(url, params=params, headers=self.headers)
                response.raise_for_status()
                data = response.json()

                results = data.get("results", {})
                serp_results = results.get("serp", [])

                competitors = []
                for result in serp_results[:limit]:
                    competitors.append({
                        "domain": result.get("domain"),
                        "title": result.get("title"),
                        "url": result.get("url"),
                        "position": result.get("position"),
                        "traffic_share": result.get("traffic_share")
                    })

                return {
                    "keyword": keyword,
                    "competitors_count": len(competitors),
                    "competitors": competitors
                }
        except httpx.HTTPError as e:
            logger.error(f"HTTP error analyzing competitors: {e}")
            raise
        except Exception as e:
            logger.error(f"Error analyzing competitors: {e}")
            raise

    async def bulk_audit_products(self, product_urls: list) -> Dict[str, Any]:
        """Audit multiple product pages"""
        logger.info(f"Bulk auditing {len(product_urls)} product pages")
        try:
            results = []
            async with httpx.AsyncClient() as client:
                for url in product_urls[:50]:  # Limit to 50 per request
                    try:
                        audit_result = await self.audit_product_page(url)
                        results.append(audit_result)
                    except Exception as e:
                        logger.warning(f"Error auditing {url}: {e}")
                        results.append({"url": url, "error": str(e)})

            return {
                "total_urls": len(product_urls),
                "audited": len([r for r in results if "error" not in r]),
                "results": results
            }
        except Exception as e:
            logger.error(f"Error in bulk audit: {e}")
            raise

    async def get_seo_recommendations(self, product_url: str) -> Dict[str, Any]:
        """Get SEO optimization recommendations based on audit"""
        logger.info(f"Getting SEO recommendations for: {product_url}")
        try:
            # First audit the page
            audit = await self.audit_product_page(product_url)

            # Generate recommendations based on metrics
            recommendations = []
            domain_rating = audit.get("domain_rating", 0)
            organic_traffic = audit.get("organic_search_traffic", 0)

            if (domain_rating or 0) < 20:
                recommendations.append({
                    "priority": "high",
                    "recommendation": "Build more high-quality backlinks",
                    "reason": "Low domain authority",
                    "impact": "Improves search rankings significantly"
                })

            if (organic_traffic or 0) < 100:
                recommendations.append({
                    "priority": "high",
                    "recommendation": "Improve on-page SEO and content quality",
                    "reason": "Low organic search traffic",
                    "impact": "Increases visibility in search results"
                })

            recommendations.append({
                "priority": "medium",
                "recommendation": "Analyze competitor content strategies",
                "reason": "Stay competitive in your niche",
                "impact": "Helps identify content gaps and opportunities"
            })

            return {
                "url": product_url,
                "audit_metrics": audit,
                "recommendations": recommendations
            }
        except Exception as e:
            logger.error(f"Error getting recommendations: {e}")
            raise

# Initialize client
seo_client = SEOClient()
