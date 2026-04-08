"""
Shopify MCP Tools
Exposes Shopify data and operations as MCP tools
"""

import logging
import asyncio
import uuid
import time
from typing import Any, Dict
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field
from .client import shopify_client
from .actions import actions as shopify_actions

# In-memory job tracker for background SEO jobs
_seo_jobs: Dict[str, Dict] = {}

logger = logging.getLogger(__name__)

# Input schemas
class SalesReportInput(BaseModel):
    days: int = Field(30, description="Number of days to fetch sales for")
    include_details: bool = Field(True, description="Include detailed product breakdown")

class InventoryCheckInput(BaseModel):
    low_stock_threshold: int = Field(10, description="Alert if stock below this number")

# Register Shopify tools
def register_shopify_tools(server: FastMCP):
    """Register all Shopify-related tools with the MCP server"""

    @server.tool()
    async def get_sales_report(days: int = 30) -> Dict[str, Any]:
        """
        Get sales metrics for your Shopify store.

        Returns: Total sales, order count, average order value (no raw order list to keep response small).
        """
        logger.info(f"Tool called: get_sales_report (days={days})")
        try:
            data = await shopify_client.get_sales_data(days=days)
            return {
                "status": "success",
                "period_days": data.get("period_days"),
                "total_orders": data.get("total_orders"),
                "total_revenue": data.get("total_revenue"),
                "average_order_value": data.get("average_order_value"),
                "currency": data.get("currency"),
                "message": f"Sales data for last {days} days"
            }
        except Exception as e:
            logger.error(f"Error fetching sales data: {e}")
            return {
                "status": "error",
                "message": f"Failed to fetch sales data: {str(e)}"
            }

    @server.tool()
    async def get_inventory_status(low_stock_threshold: int = 10) -> Dict[str, Any]:
        """
        Check current inventory levels and alert on low stock.

        Returns: Summary with counts and list of low-stock items only (not full inventory).
        """
        logger.info(f"Tool called: get_inventory_status (threshold={low_stock_threshold})")
        try:
            data = await shopify_client.get_inventory()
            inventory_levels = data.get("inventory_levels", [])

            # Build low-stock summary only (keep payload small)
            low_stock = [
                {
                    "inventory_item_id": item.get("inventory_item_id"),
                    "location_id": item.get("location_id"),
                    "available": item.get("available", 0)
                }
                for item in inventory_levels
                if (item.get("available") or 0) < low_stock_threshold
            ]

            return {
                "status": "success",
                "total_locations": data.get("total_locations", 0),
                "total_inventory_items": data.get("total_inventory_items", 0),
                "low_stock_count": len(low_stock),
                "low_stock_threshold": low_stock_threshold,
                "low_stock_items": low_stock[:50],  # cap at 50 items
                "message": f"{len(low_stock)} items below threshold of {low_stock_threshold}"
            }
        except Exception as e:
            logger.error(f"Error fetching inventory: {e}")
            return {
                "status": "error",
                "message": f"Failed to fetch inventory: {str(e)}"
            }

    @server.tool()
    async def get_product_count() -> Dict[str, Any]:
        """
        Get the exact total number of products in the store, broken down by status.

        Use this when the user asks how many products they have.
        Returns: Total count, active count, draft count.
        """
        logger.info("Tool called: get_product_count")
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                total = (await client.get(f"{shopify_client.base_url}/products/count.json", headers=shopify_client.headers)).json().get("count", 0)
                active = (await client.get(f"{shopify_client.base_url}/products/count.json?status=active", headers=shopify_client.headers)).json().get("count", 0)
                draft = (await client.get(f"{shopify_client.base_url}/products/count.json?status=draft", headers=shopify_client.headers)).json().get("count", 0)
            return {
                "status": "success",
                "total_products": total,
                "active_products": active,
                "draft_products": draft
            }
        except Exception as e:
            logger.error(f"Error fetching product count: {e}")
            return {"status": "error", "message": str(e)}

    @server.tool()
    async def get_top_products(limit: int = 10) -> Dict[str, Any]:
        """
        Get a list of products from the store (not a count).
        Use get_product_count instead if the user only wants to know how many products they have.

        Returns: List of products with key details. Max 250 per call.
        """
        logger.info(f"Tool called: get_top_products (limit={limit})")
        try:
            products = await shopify_client.get_products(limit=min(limit, 50))
            raw = products.get("products", [])
            # Return only essential fields to keep payload small
            slim = [
                {
                    "id": p.get("id"),
                    "title": p.get("title"),
                    "handle": p.get("handle"),
                    "status": p.get("status"),
                    "vendor": p.get("vendor"),
                    "product_type": p.get("product_type"),
                }
                for p in raw
            ]
            return {
                "status": "success",
                "total_products_in_store": products.get("total_products_in_store", 0),
                "products_returned": len(slim),
                "products": slim,
            }
        except Exception as e:
            logger.error(f"Error fetching top products: {e}")
            return {
                "status": "error",
                "message": f"Failed to fetch products: {str(e)}"
            }

    @server.tool()
    async def get_recent_orders(limit: int = 20) -> Dict[str, Any]:
        """
        Get recent orders from your Shopify store.

        Returns: List of recent orders with key details (capped at 20 to keep response size manageable).
        """
        logger.info(f"Tool called: get_recent_orders (limit={limit})")
        try:
            orders = await shopify_client.get_orders(limit=min(limit, 20))
            raw = orders.get("orders", [])
            slim = [
                {
                    "id": o.get("id"),
                    "order_number": o.get("order_number"),
                    "created_at": o.get("created_at"),
                    "total_price": o.get("total_price"),
                    "currency": o.get("currency"),
                    "financial_status": o.get("financial_status"),
                    "fulfillment_status": o.get("fulfillment_status"),
                    "customer_email": o.get("customer", {}).get("email") if o.get("customer") else None,
                    "item_count": len(o.get("line_items", [])),
                }
                for o in raw
            ]
            return {
                "status": "success",
                "count": len(slim),
                "orders": slim,
            }
        except Exception as e:
            logger.error(f"Error fetching orders: {e}")
            return {
                "status": "error",
                "message": f"Failed to fetch orders: {str(e)}"
            }

    @server.tool()
    async def update_product_seo(
        product_id: str,
        meta_title: str,
        meta_description: str
    ) -> Dict[str, Any]:
        """
        Update the SEO meta title and meta description for a Shopify product.

        Use this after generating optimized SEO copy to apply the changes directly to the store.
        product_id: The numeric Shopify product ID (get it from get_top_products).
        meta_title: SEO title (50-60 characters recommended).
        meta_description: SEO meta description (150-160 characters recommended).
        """
        logger.info(f"Tool called: update_product_seo (product_id={product_id})")
        try:
            result = await shopify_actions.update_product_seo(
                product_id=product_id,
                seo_updates={"meta_title": meta_title, "meta_description": meta_description}
            )
            if result.get("success"):
                return {
                    "status": "success",
                    "product_id": product_id,
                    "meta_title": meta_title,
                    "meta_description": meta_description,
                    "message": f"SEO updated for product {product_id}"
                }
            else:
                return {"status": "error", "message": result.get("error", "Unknown error")}
        except Exception as e:
            logger.error(f"Error updating product SEO: {e}")
            return {"status": "error", "message": str(e)}

    @server.tool()
    async def create_blog_article(
        topic: str,
        keywords: str = "",
        tags: str = "",
    ) -> Dict[str, Any]:
        """
        Generate and publish a complete SEO-optimized blog article to the Shopify store.

        This tool writes the full content internally using the API key — do NOT write the
        content yourself in the conversation. Just provide the topic and keywords.
        topic: What the blog post should be about (e.g. "kitchen storage tips").
        keywords: Comma-separated target keywords (e.g. "storage jars, kitchen organization").
        tags: Comma-separated Shopify tags (e.g. "kitchen,tips,organization").
        """
        logger.info(f"Tool called: create_blog_article (topic={topic!r})")
        try:
            keyword_list = [k.strip() for k in keywords.split(",") if k.strip()] if keywords else []
            tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []

            # Generate content via API key (not conversation tokens)
            draft = await shopify_actions.draft_blog_content(topic=topic, keywords=keyword_list)
            if not draft.get("success"):
                return {"status": "error", "message": f"Content generation failed: {draft.get('error')}"}

            blog = draft["blog"]
            result = await shopify_actions.publish_blog(
                title=blog.get("title", topic),
                content=blog.get("content", ""),
                tags=tag_list or blog.get("tags", []),
                meta_title=blog.get("meta_title", ""),
                meta_description=blog.get("meta_description", ""),
            )
            if result.get("success"):
                return {
                    "status": "success",
                    "article_id": result.get("article_id"),
                    "title": result.get("title"),
                    "blog": result.get("blog_title"),
                    "url": result.get("url"),
                    "published_at": result.get("published_at"),
                    "meta_title": blog.get("meta_title"),
                    "meta_description": blog.get("meta_description"),
                    "message": f"Article published: {result.get('url')}",
                }
            else:
                return {"status": "error", "message": result.get("error", "Unknown error")}
        except Exception as e:
            logger.error(f"Error creating blog article: {e}")
            return {"status": "error", "message": str(e)}

    @server.tool()
    async def bulk_update_seo(
        updates: list,
    ) -> Dict[str, Any]:
        """
        Update SEO titles and meta descriptions for multiple products in one call.

        Use this instead of calling update_product_seo repeatedly.
        updates: list of objects, each with:
          - product_id (str): the Shopify product ID
          - meta_title (str): SEO title
          - meta_description (str): SEO meta description

        Example:
        [
          {"product_id": "123", "meta_title": "Best Slicer", "meta_description": "..."},
          {"product_id": "456", "meta_title": "Storage Jar", "meta_description": "..."}
        ]
        """
        logger.info(f"Tool called: bulk_update_seo ({len(updates)} products)")
        results = []
        success_count = 0
        fail_count = 0

        for item in updates:
            product_id = str(item.get("product_id", ""))
            meta_title = item.get("meta_title", "")
            meta_description = item.get("meta_description", "")

            if not product_id:
                results.append({"product_id": product_id, "status": "error", "message": "Missing product_id"})
                fail_count += 1
                continue

            try:
                result = await shopify_actions.update_product_seo(
                    product_id=product_id,
                    seo_updates={"meta_title": meta_title, "meta_description": meta_description}
                )
                if result.get("success"):
                    results.append({"product_id": product_id, "status": "success", "meta_title": meta_title})
                    success_count += 1
                else:
                    results.append({"product_id": product_id, "status": "error", "message": result.get("error")})
                    fail_count += 1
            except Exception as e:
                results.append({"product_id": product_id, "status": "error", "message": str(e)})
                fail_count += 1

        return {
            "status": "done",
            "total": len(updates),
            "success": success_count,
            "failed": fail_count,
            "results": results,
        }

    @server.tool()
    async def seo_update_all_products(
        status: str = "active",
        dry_run: bool = False,
    ) -> Dict[str, Any]:
        """
        Start a background job that generates and applies SEO for ALL products in the store.

        Returns immediately with a job_id. Use check_seo_job(job_id) to monitor progress.
        Safe for stores with 500+ products — runs entirely server-side with no context limit.

        status: "active" (default), "draft", or "any"
        dry_run: true = preview only, do NOT save changes
        """
        job_id = str(uuid.uuid4())[:8]
        _seo_jobs[job_id] = {
            "status": "running",
            "started_at": time.time(),
            "total": 0,
            "success": 0,
            "failed": 0,
            "dry_run": dry_run,
            "message": "Starting...",
        }

        async def _run():
            try:
                result = await shopify_actions.bulk_seo_all_products(
                    status=status,
                    batch_size=10,
                    dry_run=dry_run,
                )
                _seo_jobs[job_id].update({
                    "status": "done",
                    "total": result.get("total_products", 0),
                    "success": result.get("success", 0),
                    "failed": result.get("failed", 0),
                    "message": result.get("message", "Completed"),
                    "sample_results": result.get("results", [])[:20],
                })
            except Exception as e:
                logger.error(f"SEO job {job_id} failed: {e}", exc_info=True)
                _seo_jobs[job_id].update({"status": "error", "message": str(e)})

        asyncio.create_task(_run())
        logger.info(f"SEO job {job_id} started in background")

        return {
            "status": "started",
            "job_id": job_id,
            "message": f"SEO job started for all {status} products. Use check_seo_job('{job_id}') to monitor progress.",
            "dry_run": dry_run,
        }

    @server.tool()
    async def check_seo_job(job_id: str) -> Dict[str, Any]:
        """
        Check the progress of a background SEO update job started by seo_update_all_products.

        job_id: The ID returned when you started the job.
        """
        logger.info(f"Tool called: check_seo_job ({job_id})")
        job = _seo_jobs.get(job_id)
        if not job:
            return {"status": "error", "message": f"No job found with ID '{job_id}'"}

        elapsed = round(time.time() - job["started_at"], 1)
        return {
            "job_id": job_id,
            "status": job["status"],
            "elapsed_seconds": elapsed,
            "total": job.get("total", 0),
            "success": job.get("success", 0),
            "failed": job.get("failed", 0),
            "dry_run": job.get("dry_run", False),
            "message": job.get("message", ""),
            "sample_results": job.get("sample_results", []),
        }

    @server.tool()
    async def list_store_pages() -> Dict[str, Any]:
        """
        List all pages on the Shopify store (Privacy Policy, About Us, FAQ, etc).

        Returns page IDs, titles, and handles needed for update_store_page.
        """
        logger.info("Tool called: list_store_pages")
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"{shopify_client.base_url}/pages.json?fields=id,title,handle,updated_at&limit=100",
                    headers=shopify_client.headers
                )
                resp.raise_for_status()
                pages = resp.json().get("pages", [])
                return {
                    "status": "success",
                    "count": len(pages),
                    "pages": pages,
                }
        except Exception as e:
            logger.error(f"Error listing pages: {e}")
            return {"status": "error", "message": str(e)}

    @server.tool()
    async def get_store_page(page_id: str) -> Dict[str, Any]:
        """
        Get the full content of a store page by its ID.

        Use list_store_pages first to find the page ID.
        """
        logger.info(f"Tool called: get_store_page ({page_id})")
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"{shopify_client.base_url}/pages/{page_id}.json",
                    headers=shopify_client.headers
                )
                resp.raise_for_status()
                page = resp.json().get("page", {})
                return {
                    "status": "success",
                    "id": page.get("id"),
                    "title": page.get("title"),
                    "handle": page.get("handle"),
                    "body_html": page.get("body_html"),
                    "updated_at": page.get("updated_at"),
                }
        except Exception as e:
            logger.error(f"Error getting page: {e}")
            return {"status": "error", "message": str(e)}

    @server.tool()
    async def update_store_page(
        page_id: str,
        title: str = "",
        body_html: str = "",
    ) -> Dict[str, Any]:
        """
        Update the title and/or content of a Shopify store page.

        Use this to update Privacy Policy, About Us, FAQ, Terms of Service, or any other page.
        page_id: The numeric page ID (get it from list_store_pages).
        title: New page title (leave empty to keep existing).
        body_html: Full page content in HTML (leave empty to keep existing).
        """
        logger.info(f"Tool called: update_store_page ({page_id})")
        try:
            import httpx
            payload: Dict[str, Any] = {"page": {"id": page_id}}
            if title:
                payload["page"]["title"] = title
            if body_html:
                payload["page"]["body_html"] = body_html

            async with httpx.AsyncClient() as client:
                resp = await client.put(
                    f"{shopify_client.base_url}/pages/{page_id}.json",
                    json=payload,
                    headers=shopify_client.headers
                )
                resp.raise_for_status()
                page = resp.json().get("page", {})
                return {
                    "status": "success",
                    "page_id": page.get("id"),
                    "title": page.get("title"),
                    "handle": page.get("handle"),
                    "updated_at": page.get("updated_at"),
                    "message": f"Page '{page.get('title')}' updated successfully",
                }
        except Exception as e:
            logger.error(f"Error updating page: {e}")
            return {"status": "error", "message": str(e)}

    @server.tool()
    async def update_store_policy(
        policy_type: str,
        body_html: str,
    ) -> Dict[str, Any]:
        """
        Update a Shopify store policy page (Refund Policy, Privacy Policy, Terms of Service, etc).

        policy_type must be one of:
          - REFUND_POLICY
          - PRIVACY_POLICY
          - TERMS_OF_SERVICE
          - SHIPPING_POLICY
          - LEGAL_NOTICE
          - SUBSCRIPTION_POLICY

        body_html: Full policy content in HTML format.
        """
        logger.info(f"Tool called: update_store_policy (type={policy_type})")
        valid_types = {"REFUND_POLICY", "PRIVACY_POLICY", "TERMS_OF_SERVICE", "SHIPPING_POLICY", "LEGAL_NOTICE", "SUBSCRIPTION_POLICY"}
        if policy_type not in valid_types:
            return {"status": "error", "message": f"Invalid policy_type. Must be one of: {', '.join(valid_types)}"}

        import httpx
        graphql_url = f"https://{shopify_client.store_url}/admin/api/2024-10/graphql.json"
        headers = {**shopify_client.headers, "Content-Type": "application/json"}

        mutation = """
        mutation shopPolicyUpdate($shopPolicy: ShopPolicyInput!) {
          shopPolicyUpdate(shopPolicy: $shopPolicy) {
            userErrors { field message }
            shopPolicy { type url }
          }
        }
        """
        variables = {"shopPolicy": {"type": policy_type, "body": body_html}}

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    graphql_url,
                    json={"query": mutation, "variables": variables},
                    headers=headers,
                )
                resp.raise_for_status()
                data = resp.json()

                errors = data.get("data", {}).get("shopPolicyUpdate", {}).get("userErrors", [])
                if errors:
                    return {"status": "error", "message": errors}

                policy = data.get("data", {}).get("shopPolicyUpdate", {}).get("shopPolicy", {})
                return {
                    "status": "success",
                    "policy_type": policy_type,
                    "url": policy.get("url"),
                    "message": f"{policy_type} updated successfully",
                }
        except Exception as e:
            logger.error(f"Error updating policy: {e}")
            return {"status": "error", "message": str(e)}

    logger.info("Shopify tools registered")
