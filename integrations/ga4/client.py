"""
Google Analytics 4 API Client
Handles GA4 authentication via OAuth and API calls
"""

import logging
from typing import Any, Dict
from datetime import datetime, timedelta
import httpx
from config.settings import GA4_PROPERTY_ID
from integrations.google_auth import get_access_token, refresh_tokens, is_token_expired

logger = logging.getLogger(__name__)

class GA4Client:
    """Google Analytics 4 API client with shared Google OAuth"""

    def __init__(self):
        self.property_id = GA4_PROPERTY_ID

    async def _get_headers(self) -> Dict[str, str]:
        token = get_access_token()
        if not token:
            raise RuntimeError("Not authenticated with Google")
        return {"Authorization": f"Bearer {token}"}

    async def _request(self, url: str, payload: dict) -> dict:
        """Make an authenticated GA4 API request, proactively refreshing expired tokens"""
        if is_token_expired():
            await refresh_tokens()
        headers = await self._get_headers()
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            if response.status_code in (401, 403):
                await refresh_tokens()
                headers = await self._get_headers()
                response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()

    async def get_traffic_report(self, days: int = 30) -> Dict[str, Any]:
        """Get traffic metrics for the last N days"""
        logger.info(f"Fetching traffic data for last {days} days")
        try:
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            url = f"https://analyticsdata.googleapis.com/v1beta/properties/{self.property_id}:runReport"
            data = await self._request(url, {
                "dateRanges": [{"startDate": start_date, "endDate": end_date}],
                "metrics": [
                    {"name": "activeUsers"},
                    {"name": "sessions"},
                    {"name": "screenPageViews"},
                    {"name": "bounceRate"}
                ]
            })
            rows = data.get("rows", [])
            if rows:
                metrics = rows[0].get("metricValues", [])
                return {
                    "period_days": days,
                    "active_users": int(metrics[0].get("value", 0)) if len(metrics) > 0 else 0,
                    "sessions": int(metrics[1].get("value", 0)) if len(metrics) > 1 else 0,
                    "page_views": int(metrics[2].get("value", 0)) if len(metrics) > 2 else 0,
                    "bounce_rate": float(metrics[3].get("value", 0)) if len(metrics) > 3 else 0.0
                }
            return {"error": "No data available"}
        except Exception as e:
            logger.error(f"Error fetching traffic: {e}")
            return {"error": str(e)}

    async def get_conversion_metrics(self, days: int = 30) -> Dict[str, Any]:
        """Get conversion rate and conversion data"""
        logger.info(f"Fetching conversion metrics for last {days} days")
        try:
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            url = f"https://analyticsdata.googleapis.com/v1beta/properties/{self.property_id}:runReport"
            data = await self._request(url, {
                "dateRanges": [{"startDate": start_date, "endDate": end_date}],
                "metrics": [
                    {"name": "conversions"},
                    {"name": "conversionRate"},
                    {"name": "ecommercePurchases"},
                    {"name": "totalRevenue"}
                ]
            })
            rows = data.get("rows", [])
            if rows:
                metrics = rows[0].get("metricValues", [])
                return {
                    "period_days": days,
                    "conversions": int(metrics[0].get("value", 0)) if len(metrics) > 0 else 0,
                    "conversion_rate": float(metrics[1].get("value", 0)) if len(metrics) > 1 else 0.0,
                    "purchases": int(metrics[2].get("value", 0)) if len(metrics) > 2 else 0,
                    "revenue": float(metrics[3].get("value", 0)) if len(metrics) > 3 else 0.0
                }
            return {"error": "No data available"}
        except Exception as e:
            logger.error(f"Error fetching conversions: {e}")
            return {"error": str(e)}

    async def get_user_engagement(self, days: int = 30) -> Dict[str, Any]:
        """Get user engagement metrics"""
        logger.info(f"Fetching user engagement for last {days} days")
        try:
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            url = f"https://analyticsdata.googleapis.com/v1beta/properties/{self.property_id}:runReport"
            data = await self._request(url, {
                "dateRanges": [{"startDate": start_date, "endDate": end_date}],
                "metrics": [
                    {"name": "sessionDuration"},
                    {"name": "scrolledUsers"},
                    {"name": "engagedSessions"},
                    {"name": "engagementRate"}
                ]
            })
            rows = data.get("rows", [])
            if rows:
                metrics = rows[0].get("metricValues", [])
                return {
                    "period_days": days,
                    "avg_session_duration": float(metrics[0].get("value", 0)) if len(metrics) > 0 else 0.0,
                    "scrolled_users": int(metrics[1].get("value", 0)) if len(metrics) > 1 else 0,
                    "engaged_sessions": int(metrics[2].get("value", 0)) if len(metrics) > 2 else 0,
                    "engagement_rate": float(metrics[3].get("value", 0)) if len(metrics) > 3 else 0.0
                }
            return {"error": "No data available"}
        except Exception as e:
            logger.error(f"Error fetching engagement: {e}")
            return {"error": str(e)}

    async def get_top_pages(self, limit: int = 10) -> Dict[str, Any]:
        """Get top pages by traffic"""
        logger.info(f"Fetching top {limit} pages")
        try:
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
            url = f"https://analyticsdata.googleapis.com/v1beta/properties/{self.property_id}:runReport"
            data = await self._request(url, {
                "dateRanges": [{"startDate": start_date, "endDate": end_date}],
                "metrics": [{"name": "screenPageViews"}],
                "dimensions": [{"name": "pagePath"}],
                "limit": limit,
                "orderBys": [{"metric": {"metricName": "screenPageViews"}, "desc": True}]
            })
            rows = data.get("rows", [])
            top_pages = []
            for row in rows:
                dimension_values = row.get("dimensionValues", [])
                metric_values = row.get("metricValues", [])
                top_pages.append({
                    "page": dimension_values[0].get("value", "") if dimension_values else "",
                    "views": int(metric_values[0].get("value", 0)) if metric_values else 0
                })
            return {"top_pages": top_pages, "total_pages": len(top_pages)}
        except Exception as e:
            logger.error(f"Error fetching top pages: {e}")
            return {"error": str(e)}

# Initialize client
ga4_client = GA4Client()
