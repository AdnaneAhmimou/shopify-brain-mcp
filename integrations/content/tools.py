"""
Content Pipeline Tools
Chains Shopify → scenario writing → Higgsfield Seedance video → Simplified social publishing
"""

import logging
import re
import httpx
import os
from typing import Any, Dict, List, Optional
from mcp.server.fastmcp import FastMCP
from . import simplified_client

logger = logging.getLogger(__name__)


def _shopify_headers() -> dict:
    return {"X-Shopify-Access-Token": os.getenv("SHOPIFY_ACCESS_TOKEN", "")}


def _shopify_base() -> str:
    store = os.getenv("SHOPIFY_STORE_URL", "")
    version = os.getenv("SHOPIFY_API_VERSION", "2024-10")
    return f"https://{store}/admin/api/{version}"


def _strip_html(html: str) -> str:
    return re.sub(r"<[^>]+>", "", html or "").strip()


def register_content_tools(server: FastMCP):

    @server.tool()
    async def get_viral_products(limit: int = 10) -> Dict[str, Any]:
        """
        Pull the most recently added products from Shopify with their images and descriptions.
        Returns product ID, title, description, image URLs, and handle for each product.
        Use this to find candidates for video content creation.

        limit: number of products to return (default 10)
        """
        try:
            async with httpx.AsyncClient(timeout=20) as client:
                r = await client.get(
                    f"{_shopify_base()}/products.json",
                    headers=_shopify_headers(),
                    params={
                        "limit": limit,
                        "order": "created_at desc",
                        "fields": "id,title,body_html,images,handle,variants",
                    },
                )
                r.raise_for_status()
                products = r.json().get("products", [])

            result = []
            for p in products:
                images = [img["src"] for img in p.get("images", [])]
                price = (p.get("variants") or [{}])[0].get("price", "")
                # Build numbered image map so URLs are always surfaced as text
                image_map = {f"image_{i+1}": url for i, url in enumerate(images)}
                result.append({
                    "id": str(p["id"]),
                    "title": p["title"],
                    "description": _strip_html(p.get("body_html", ""))[:400],
                    "image_urls": image_map,
                    "primary_image_url": images[0] if images else None,
                    "total_images": len(images),
                    "handle": p.get("handle", ""),
                    "price": price,
                    "store_url": f"https://{os.getenv('SHOPIFY_STORE_URL', '')}/products/{p.get('handle', '')}",
                    "IMPORTANT": "Always display all image_urls as plain text links to the user",
                })

            return {"status": "success", "count": len(result), "products": result}

        except Exception as e:
            logger.error(f"get_viral_products error: {e}")
            return {"status": "error", "message": str(e)}

    @server.tool()
    async def generate_video_scenarios(
        product_id: str,
        num_scenarios: int = 3,
    ) -> Dict[str, Any]:
        """
        Generate 3 detailed 15-second Ad/UGC video scenarios for a product.
        Each scenario is fully scripted: shot-by-shot breakdown, Seedance prompt,
        audio direction (voiceover script OR music mood), caption, and hashtags.

        product_id: Shopify product ID (get from get_viral_products)
        num_scenarios: number of scenarios to generate (default 3)

        NOTE: Present all scenarios clearly to the user. Ask which one to generate.
        Then call prepare_higgsfield_job with duration=15.
        """
        try:
            async with httpx.AsyncClient(timeout=20) as client:
                r = await client.get(
                    f"{_shopify_base()}/products/{product_id}.json",
                    headers=_shopify_headers(),
                    params={"fields": "id,title,body_html,images,handle,variants"},
                )
                r.raise_for_status()
                p = r.json().get("product", {})

            title = p.get("title", "")
            description = _strip_html(p.get("body_html", ""))
            images = [img["src"] for img in p.get("images", [])]
            handle = p.get("handle", "")
            price = (p.get("variants") or [{}])[0].get("price", "")
            store_url = f"https://{os.getenv('SHOPIFY_STORE_URL', '')}/products/{handle}"

            image_map = {f"image_{i+1}": url for i, url in enumerate(images)}

            return {
                "status": "success",
                "video_duration": "15 seconds",
                "instruction": (
                    f"Generate {num_scenarios} highly detailed 15-second Ad/UGC video scenarios for this product. "
                    f"Scenarios must be varied in style: "
                    f"  Scenario 1 — PAID AD: polished, brand-forward, aspirational lifestyle. "
                    f"  Scenario 2 — UGC AD: raw, authentic, person-on-camera unboxing or real-use moment, feels organic. "
                    f"  Scenario 3 — CINEMATIC/DRAMATIC: high-production visual storytelling, emotion-driven, no talking. "
                    f"\n\nFor EACH scenario provide ALL of these fields:\n"
                    f"(1) 'scenario_number': 1, 2, or 3\n"
                    f"(2) 'ad_type': 'Paid Ad' | 'UGC Ad' | 'Cinematic'\n"
                    f"(3) 'scene_title': catchy short title\n"
                    f"(4) 'full_script': A complete second-by-second breakdown of the 15-second video. "
                    f"    Format: [0-3s] what happens, [3-7s] what happens, [7-11s] what happens, [11-15s] CTA/ending. "
                    f"    Be very specific: describe the person, their action, what they say or do, environment, props, camera angle.\n"
                    f"(5) 'seedance_prompt': An extremely detailed Higgsfield Seedance image-to-video prompt. "
                    f"    Must include: exact camera movement (slow push-in / orbit / handheld shake / dolly), "
                    f"    lighting setup (golden hour / soft box / harsh sunlight / neon), "
                    f"    subject action (what the person/product does frame by frame), "
                    f"    background environment, visual style (cinematic 4K / raw iPhone UGC / editorial fashion). "
                    f"    Minimum 5 sentences. Make it feel like a real director's brief.\n"
                    f"(6) 'audio_type': 'voiceover' OR 'music' — choose what fits the scenario best. "
                    f"    UGC Ads should almost always use 'voiceover' (person talking on camera). "
                    f"    Cinematic/Paid Ads can use 'music'.\n"
                    f"(7) 'voiceover_script': If audio_type is 'voiceover', write the FULL word-for-word script the person says "
                    f"    in the video (must fit within 15 seconds, about 35-45 words). "
                    f"    If audio_type is 'music', write 'N/A'.\n"
                    f"(8) 'music_direction': If audio_type is 'music', describe the exact music mood, tempo, genre, instruments "
                    f"    (e.g. 'upbeat lo-fi hip-hop with soft piano, 95 BPM, energetic but warm'). "
                    f"    If audio_type is 'voiceover', write 'N/A'.\n"
                    f"(9) 'best_image': which image number (image_1 through image_{len(images)}) works best and why\n"
                    f"(10) 'hook': the first 3-second hook line or visual that stops the scroll\n"
                    f"(11) 'cta': the call-to-action text shown at the end (e.g. 'Shop now at arbasa.com')\n"
                    f"(12) 'caption': social media caption with emojis (150 chars max)\n"
                    f"(13) 'hashtags': 8-10 relevant hashtags\n"
                    f"\nIMPORTANT: Always display all image URLs as plain clickable text. "
                    f"After presenting scenarios, ask: which scenario + which image?"
                ),
                "product": {
                    "id": product_id,
                    "title": title,
                    "description": description[:600],
                    "price": price,
                    "store_url": store_url,
                },
                "product_images": image_map,
                "total_images": len(images),
                "DISPLAY_INSTRUCTIONS": "Show every image URL from product_images as plain text — do not embed as markdown images",
            }

        except Exception as e:
            logger.error(f"generate_video_scenarios error: {e}")
            return {"status": "error", "message": str(e)}

    @server.tool()
    async def prepare_higgsfield_job(
        product_id: str,
        seedance_prompt: str,
        image_url: Optional[str] = None,
        duration: int = 15,
        aspect_ratio: str = "9:16",
    ) -> Dict[str, Any]:
        """
        Prepares everything needed for Higgsfield video generation via browser (Playwright MCP).
        Returns the exact image URL, prompt, and settings to use in Higgsfield.

        Call this after the user picks a scenario from generate_video_scenarios.
        Then use Playwright MCP to open Higgsfield, upload the image, paste the prompt, and generate.
        Once Higgsfield finishes, grab the CDN video URL and pass it to post_to_social.

        product_id: Shopify product ID
        seedance_prompt: the Seedance prompt from the chosen scenario
        image_url: product image URL to use (auto-fetches primary image if not provided)
        duration: 5 or 10 seconds
        aspect_ratio: "9:16" vertical (recommended) | "16:9" landscape | "1:1" square
        """
        try:
            # Fetch product to get image if not provided
            async with httpx.AsyncClient(timeout=20) as client:
                r = await client.get(
                    f"{_shopify_base()}/products/{product_id}.json",
                    headers=_shopify_headers(),
                    params={"fields": "id,title,images,handle"},
                )
                r.raise_for_status()
                product = r.json().get("product", {})

            images = [img["src"] for img in product.get("images", [])]
            image_map = {f"image_{i+1}": url for i, url in enumerate(images)}
            selected_image = image_url or (images[0] if images else None)
            handle = product.get("handle", "")
            store_url = f"https://{os.getenv('SHOPIFY_STORE_URL', '')}/products/{handle}"

            return {
                "status": "ready",
                "next_step": "Use Playwright MCP to open Higgsfield and generate the video",
                "higgsfield_instructions": {
                    "url": "https://higgsfield.ai/video",
                    "model": "Seedance 2.0",
                    "mode": "Image-to-Video",
                    "upload_this_image": selected_image,
                    "paste_this_prompt": seedance_prompt,
                    "duration_seconds": duration,
                    "aspect_ratio": aspect_ratio,
                    "after_generation": "Copy the video CDN URL and pass it to post_to_social",
                },
                "product": {
                    "id": product_id,
                    "title": product.get("title", ""),
                    "store_url": store_url,
                    "all_image_urls": image_map,
                },
            }

        except Exception as e:
            logger.error(f"prepare_higgsfield_job error: {e}")
            return {"status": "error", "message": str(e)}

    @server.tool()
    async def get_social_accounts(network: Optional[str] = None) -> Dict[str, Any]:
        """
        List all connected social media accounts in Simplified.
        network: optional filter — pinterest, instagram, facebook, tiktok, linkedin, youtube, threads
        """
        try:
            data = await simplified_client.get_social_accounts(network)
            return {"status": "success", "accounts": data}
        except Exception as e:
            logger.error(f"get_social_accounts error: {e}")
            return {"status": "error", "message": str(e)}

    @server.tool()
    async def post_to_social(
        account_id: str,
        caption: str,
        media_urls: List[str],
        action: str = "add_to_queue",
        scheduled_date: Optional[str] = None,
        pinterest_board_id: Optional[str] = None,
        pinterest_title: Optional[str] = None,
        pinterest_link: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Post or schedule a video/image to social media via Simplified.

        account_id: from get_social_accounts
        caption: post text with emojis and hashtags
        media_urls: list of image or video URLs (max 10) — use the video_url from generate_video_from_scenario
        action: "add_to_queue" | "schedule" | "draft"
        scheduled_date: "YYYY-MM-DD HH:MM" — required if action="schedule"
        pinterest_board_id: Pinterest board ID to pin to
        pinterest_title: pin title
        pinterest_link: destination URL (product store URL)
        """
        extras = {}
        if pinterest_board_id:
            extras["pinterest"] = {
                "board_id": pinterest_board_id,
                "title": pinterest_title or "",
                "link": pinterest_link or "",
            }

        try:
            result = await simplified_client.create_post(
                account_id=account_id,
                message=caption,
                media_urls=media_urls,
                action=action,
                scheduled_date=scheduled_date,
                platform_extras=extras if extras else None,
            )
            return {"status": "success", "post": result}
        except Exception as e:
            logger.error(f"post_to_social error: {e}")
            return {"status": "error", "message": str(e)}
