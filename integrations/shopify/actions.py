"""
Shopify Actions - Write operations
Update products, publish content, take actions in Shopify
"""

import logging
import httpx
from typing import Any, Dict
from anthropic import Anthropic
from config.settings import SHOPIFY_ACCESS_TOKEN, SHOPIFY_API_VERSION, ANTHROPIC_API_KEY

logger = logging.getLogger(__name__)


class ShopifyActions:
    """Execute write operations on Shopify"""

    def __init__(self):
        from config.settings import SHOPIFY_STORE_URL
        raw = SHOPIFY_STORE_URL or "arbasa-7450.myshopify.com"
        if "myshopify.com" not in raw:
            store_name = raw.split(".")[0]
            self.store_url = f"{store_name}.myshopify.com"
        else:
            self.store_url = raw
        self.api_version = SHOPIFY_API_VERSION
        self.base_url = f"https://{self.store_url}/admin/api/{self.api_version}"
        self.headers = {"X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN}
        self.claude = Anthropic(api_key=ANTHROPIC_API_KEY)

    async def update_product(self, product_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update product details in Shopify

        Updates can include:
        - title: Product title
        - body_html: Product description
        - handle: URL slug
        - tags: Comma-separated tags
        - product_type: Product category
        """
        logger.info(f"Updating product {product_id}")
        try:
            async with httpx.AsyncClient() as client:
                url = f"{self.base_url}/products/{product_id}.json"

                # Prepare update payload
                payload = {"product": updates}

                response = await client.put(url, json=payload, headers=self.headers)
                response.raise_for_status()
                data = response.json()

                logger.info(f"Product {product_id} updated successfully")
                return {
                    "success": True,
                    "product_id": product_id,
                    "updated_fields": list(updates.keys()),
                    "timestamp": data.get("product", {}).get("updated_at")
                }
        except httpx.HTTPError as e:
            logger.error(f"HTTP error updating product: {e}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error(f"Error updating product: {e}")
            return {"success": False, "error": str(e)}

    async def update_product_seo(self, product_id: str, seo_updates: Dict[str, str]) -> Dict[str, Any]:
        """
        Update SEO fields for a product (meta title, meta description)
        Uses metafields API
        """
        logger.info(f"Updating SEO for product {product_id}")
        try:
            async with httpx.AsyncClient() as client:
                url = f"{self.base_url}/products/{product_id}/metafields.json"

                metafields = []
                if "meta_title" in seo_updates:
                    metafields.append({
                        "namespace": "global",
                        "key": "title_tag",
                        "value": seo_updates["meta_title"],
                        "type": "string"
                    })
                if "meta_description" in seo_updates:
                    metafields.append({
                        "namespace": "global",
                        "key": "description_tag",
                        "value": seo_updates["meta_description"],
                        "type": "string"
                    })

                for metafield in metafields:
                    payload = {"metafield": metafield}
                    response = await client.post(url, json=payload, headers=self.headers)
                    response.raise_for_status()

                logger.info(f"SEO updated for product {product_id}")
                return {
                    "success": True,
                    "product_id": product_id,
                    "seo_fields_updated": list(seo_updates.keys())
                }
        except Exception as e:
            logger.error(f"Error updating SEO: {e}")
            return {"success": False, "error": str(e)}

    async def draft_blog_content(self, topic: str, keywords: list) -> Dict[str, Any]:
        """
        Use Claude to draft blog post content based on topic and keywords
        """
        logger.info(f"Drafting blog post about: {topic}")
        try:
            # Use Claude to generate blog content
            message = self.claude.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=2000,
                messages=[
                    {
                        "role": "user",
                        "content": f"""Write a compelling blog post for an e-commerce store.

Topic: {topic}
Target Keywords: {', '.join(keywords) if keywords else 'Not specified'}

Requirements:
- SEO optimized (2000+ words)
- Include meta title (60 chars max)
- Include meta description (160 chars max)
- Engaging, sales-focused tone
- Use headers and bullet points
- Include call-to-action

Format the response as JSON with:
- title: Blog post title
- meta_title: SEO title
- meta_description: SEO description
- content: Full HTML content
- tags: Relevant tags array"""
                    }
                ]
            )

            # Parse response
            response_text = message.content[0].text

            # Extract JSON from response
            import json
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            blog_data = json.loads(response_text[start:end])

            logger.info(f"Blog content drafted: {blog_data['title']}")
            return {
                "success": True,
                "blog": blog_data
            }
        except Exception as e:
            logger.error(f"Error drafting blog: {e}")
            return {"success": False, "error": str(e)}

    async def publish_blog(
        self,
        title: str,
        content: str,
        tags: list = None,
        meta_title: str = "",
        meta_description: str = "",
    ) -> Dict[str, Any]:
        """
        Publish blog post to Shopify — creates an article on the first available blog.
        """
        logger.info(f"Publishing blog: {title}")
        try:
            async with httpx.AsyncClient() as client:
                # Get first blog
                blogs_resp = await client.get(
                    f"{self.base_url}/blogs.json", headers=self.headers
                )
                blogs_resp.raise_for_status()
                blogs = blogs_resp.json().get("blogs", [])
                if not blogs:
                    return {"success": False, "error": "No blogs found in Shopify store. Create a blog first in Shopify Admin."}

                blog_id = blogs[0]["id"]
                blog_title = blogs[0]["title"]

                # Build article payload
                article: Dict[str, Any] = {
                    "title": title,
                    "body_html": content,
                    "published": True,
                }
                if tags:
                    article["tags"] = ", ".join(tags)
                if meta_title:
                    article["metafields"] = article.get("metafields", [])
                    article["metafields"].append({
                        "namespace": "global",
                        "key": "title_tag",
                        "value": meta_title,
                        "type": "string",
                    })
                if meta_description:
                    article.setdefault("metafields", []).append({
                        "namespace": "global",
                        "key": "description_tag",
                        "value": meta_description,
                        "type": "string",
                    })

                resp = await client.post(
                    f"{self.base_url}/blogs/{blog_id}/articles.json",
                    json={"article": article},
                    headers=self.headers,
                )
                resp.raise_for_status()
                created = resp.json().get("article", {})

                logger.info(f"Blog article published: {created.get('id')} on blog '{blog_title}'")
                return {
                    "success": True,
                    "article_id": created.get("id"),
                    "title": created.get("title"),
                    "blog_id": blog_id,
                    "blog_title": blog_title,
                    "handle": created.get("handle"),
                    "published_at": created.get("published_at"),
                    "url": f"https://{self.store_url}/blogs/{blogs[0]['handle']}/{created.get('handle')}",
                }
        except httpx.HTTPError as e:
            body = ""
            try:
                body = e.response.text[:300]
            except Exception:
                pass
            logger.error(f"HTTP error publishing blog: {e} — {body}")
            return {"success": False, "error": f"{e} — {body}"}
        except Exception as e:
            logger.error(f"Error publishing blog: {e}")
            return {"success": False, "error": str(e)}

    async def bulk_seo_all_products(
        self,
        status: str = "active",
        batch_size: int = 10,
        dry_run: bool = False,
    ) -> Dict[str, Any]:
        """
        Fetch ALL products from Shopify (paginated), generate SEO for each using Claude API,
        and apply the updates directly. Runs entirely server-side — no context window needed.

        status: "active", "draft", or "any"
        batch_size: how many products to send to Claude at once for SEO generation
        dry_run: if True, generate SEO but do not apply updates (preview mode)
        """
        logger.info(f"bulk_seo_all_products: status={status}, dry_run={dry_run}")

        all_products = []

        async with httpx.AsyncClient(timeout=30) as client:
            # Paginate through all products using cursor-based pagination
            url = f"{self.base_url}/products.json"
            params = {
                "status": status,
                "limit": 250,
                "fields": "id,title,product_type,vendor,tags,body_html",
            }

            while url:
                resp = await client.get(url, params=params, headers=self.headers)
                resp.raise_for_status()
                products = resp.json().get("products", [])
                all_products.extend(products)
                logger.info(f"Fetched {len(all_products)} products so far...")

                # Check Link header for next page
                link_header = resp.headers.get("Link", "")
                next_url = None
                for part in link_header.split(","):
                    part = part.strip()
                    if 'rel="next"' in part:
                        next_url = part.split(";")[0].strip().strip("<>")
                        break

                url = next_url
                params = {}  # params are embedded in next_url

        total = len(all_products)
        logger.info(f"Total products fetched: {total}")

        if total == 0:
            return {"status": "done", "total": 0, "success": 0, "failed": 0, "message": "No products found"}

        success_count = 0
        fail_count = 0
        results = []

        # Process in batches
        for i in range(0, total, batch_size):
            batch = all_products[i:i + batch_size]
            batch_num = i // batch_size + 1
            logger.info(f"Processing batch {batch_num} ({len(batch)} products)...")

            # Build prompt for this batch
            product_lines = "\n".join(
                f'- ID:{p["id"]} | Title: {p.get("title","?")} | Type: {p.get("product_type","?")} | Vendor: {p.get("vendor","?")}'
                for p in batch
            )

            try:
                message = self.claude.messages.create(
                    model="claude-haiku-4-5-20251001",
                    max_tokens=2000,
                    messages=[{
                        "role": "user",
                        "content": f"""You are an SEO expert for an e-commerce store. Generate SEO meta titles and descriptions for these products.

Products:
{product_lines}

Return ONLY a JSON array, no extra text:
[
  {{
    "id": "product_id",
    "meta_title": "50-60 char SEO title",
    "meta_description": "150-160 char SEO description"
  }},
  ...
]

Rules:
- meta_title: max 60 chars, include main keyword, brand if relevant
- meta_description: max 160 chars, compelling, include call to action
- Use the product title/type to infer what the product is"""
                    }]
                )

                import json as _json
                raw = message.content[0].text
                start = raw.find("[")
                end = raw.rfind("]") + 1
                seo_list = _json.loads(raw[start:end])

                for seo in seo_list:
                    pid = str(seo.get("id", ""))
                    meta_title = seo.get("meta_title", "")
                    meta_description = seo.get("meta_description", "")

                    if not pid:
                        continue

                    if dry_run:
                        results.append({
                            "product_id": pid,
                            "status": "dry_run",
                            "meta_title": meta_title,
                            "meta_description": meta_description,
                        })
                        success_count += 1
                        continue

                    update_result = await self.update_product_seo(
                        product_id=pid,
                        seo_updates={"meta_title": meta_title, "meta_description": meta_description},
                    )
                    if update_result.get("success"):
                        results.append({"product_id": pid, "status": "success", "meta_title": meta_title})
                        success_count += 1
                    else:
                        results.append({"product_id": pid, "status": "error", "message": update_result.get("error")})
                        fail_count += 1

            except Exception as e:
                logger.error(f"Batch {batch_num} failed: {e}", exc_info=True)
                for p in batch:
                    results.append({"product_id": str(p["id"]), "status": "error", "message": str(e)})
                    fail_count += 1

        return {
            "status": "done",
            "total_products": total,
            "success": success_count,
            "failed": fail_count,
            "dry_run": dry_run,
            "message": f"{'[DRY RUN] ' if dry_run else ''}Updated {success_count}/{total} products",
            "results": results[:100],  # cap result list in response
        }

    async def bulk_update_products(self, updates: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Update multiple products at once

        Example:
        {
            "product_id_1": {"title": "New title", "body_html": "..."},
            "product_id_2": {"tags": "new,tags"}
        }
        """
        logger.info(f"Bulk updating {len(updates)} products")
        results = {"success": 0, "failed": 0, "updates": []}

        for product_id, product_updates in updates.items():
            result = await self.update_product(product_id, product_updates)
            if result.get("success"):
                results["success"] += 1
            else:
                results["failed"] += 1
            results["updates"].append(result)

        return results

    async def create_promotional_product(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new product in Shopify
        """
        logger.info(f"Creating product: {product_data.get('title')}")
        try:
            async with httpx.AsyncClient() as client:
                url = f"{self.base_url}/products.json"
                payload = {"product": product_data}

                response = await client.post(url, json=payload, headers=self.headers)
                response.raise_for_status()
                data = response.json()

                product_id = data.get("product", {}).get("id")
                logger.info(f"Product created: {product_id}")
                return {
                    "success": True,
                    "product_id": product_id,
                    "title": product_data.get("title")
                }
        except Exception as e:
            logger.error(f"Error creating product: {e}")
            return {"success": False, "error": str(e)}


# Initialize actions
actions = ShopifyActions()
