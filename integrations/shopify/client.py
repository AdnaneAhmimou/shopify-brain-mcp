"""
Shopify API Client
Handles all Shopify API interactions with authentication
"""

import logging
from typing import Any, Dict
from datetime import datetime, timedelta
import httpx
from config.settings import SHOPIFY_ACCESS_TOKEN, SHOPIFY_API_VERSION

logger = logging.getLogger(__name__)

class ShopifyClient:
    """Shopify API client wrapper"""

    def __init__(self):
        self.store_url = "arbasa-7450.myshopify.com"
        self.api_version = SHOPIFY_API_VERSION
        self.base_url = f"https://{self.store_url}/admin/api/{self.api_version}"
        self.headers = {"X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN}

    async def get_sales_data(self, days: int = 30) -> Dict[str, Any]:
        """Get sales metrics for the last N days"""
        logger.info(f"Fetching sales data for last {days} days")
        try:
            # Calculate date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)

            async with httpx.AsyncClient() as client:
                # Fetch orders
                url = f"{self.base_url}/orders.json"
                params = {
                    "status": "any",
                    "limit": 250,
                    "created_at_min": start_date.isoformat(),
                    "created_at_max": end_date.isoformat(),
                    "fields": "id,created_at,total_price,currency,line_items"
                }

                response = await client.get(url, params=params, headers=self.headers)
                response.raise_for_status()
                data = response.json()

                # Calculate metrics
                orders = data.get("orders", [])
                total_revenue = sum(float(order.get("total_price", 0)) for order in orders)
                total_orders = len(orders)
                avg_order_value = total_revenue / total_orders if total_orders > 0 else 0

                return {
                    "total_orders": total_orders,
                    "total_revenue": round(total_revenue, 2),
                    "average_order_value": round(avg_order_value, 2),
                    "currency": orders[0].get("currency", "USD") if orders else "USD",
                    "period_days": days,
                    "orders": orders
                }
        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching sales data: {e}")
            raise
        except Exception as e:
            logger.error(f"Error fetching sales data: {e}")
            raise

    async def get_products(self, limit: int = 100) -> Dict[str, Any]:
        """Get product list with details"""
        logger.info(f"Fetching products (limit: {limit})")
        try:
            async with httpx.AsyncClient() as client:
                # Get exact count first
                count_response = await client.get(
                    f"{self.base_url}/products/count.json", headers=self.headers
                )
                count_response.raise_for_status()
                total_count = count_response.json().get("count", 0)

                url = f"{self.base_url}/products.json"
                params = {
                    "limit": min(limit, 50),
                    "fields": "id,title,handle,status,vendor,product_type"
                }

                response = await client.get(url, params=params, headers=self.headers)
                response.raise_for_status()
                data = response.json()

                products = data.get("products", [])
                return {
                    "total_products_in_store": total_count,
                    "products_returned": len(products),
                    "products": products
                }
        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching products: {e}")
            raise
        except Exception as e:
            logger.error(f"Error fetching products: {e}")
            raise

    async def get_inventory(self) -> Dict[str, Any]:
        """Get current inventory status"""
        logger.info("Fetching inventory status")
        try:
            headers = self.headers
            async with httpx.AsyncClient() as client:
                # First get locations
                url = f"{self.base_url}/locations.json"
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                locations = response.json().get("locations", [])

                if not locations:
                    return {"total_locations": 0, "inventory_levels": []}

                # Get inventory levels for each location
                all_inventory = []
                for location in locations:
                    inv_url = f"{self.base_url}/inventory_levels.json"
                    inv_params = {"location_ids": location["id"]}
                    inv_response = await client.get(inv_url, params=inv_params, headers=headers)
                    inv_response.raise_for_status()
                    inventory_levels = inv_response.json().get("inventory_levels", [])
                    all_inventory.extend(inventory_levels)

                # Calculate low stock items (available can be None from API)
                low_stock = [item for item in all_inventory if (item.get("available") or 0) < 10]

                return {
                    "total_locations": len(locations),
                    "total_inventory_items": len(all_inventory),
                    "low_stock_items": len(low_stock),
                    "inventory_levels": all_inventory,
                    "low_stock_threshold": 10
                }
        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching inventory: {e}")
            raise
        except Exception as e:
            logger.error(f"Error fetching inventory: {e}")
            raise

    async def get_orders(self, limit: int = 50, status: str = "any") -> Dict[str, Any]:
        """Get recent orders"""
        logger.info(f"Fetching {limit} orders with status: {status}")
        try:
            async with httpx.AsyncClient() as client:
                url = f"{self.base_url}/orders.json"
                params = {
                    "status": status,
                    "limit": min(limit, 250),
                    "order": "created_at DESC",
                    "fields": "id,created_at,updated_at,order_number,total_price,currency,financial_status,fulfillment_status,customer,line_items"
                }

                response = await client.get(url, params=params, headers=self.headers)
                response.raise_for_status()
                data = response.json()

                orders = data.get("orders", [])
                return {
                    "count": len(orders),
                    "status": status,
                    "orders": orders
                }
        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching orders: {e}")
            raise
        except Exception as e:
            logger.error(f"Error fetching orders: {e}")
            raise

    async def get_order_details(self, order_id: str) -> Dict[str, Any]:
        """Get detailed order information"""
        logger.info(f"Fetching details for order {order_id}")
        try:
            async with httpx.AsyncClient() as client:
                url = f"{self.base_url}/orders/{order_id}.json"

                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                data = response.json()

                order = data.get("order", {})
                return {
                    "order_id": order_id,
                    "order": order
                }
        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching order details: {e}")
            raise
        except Exception as e:
            logger.error(f"Error fetching order details: {e}")
            raise

# Initialize client
shopify_client = ShopifyClient()
