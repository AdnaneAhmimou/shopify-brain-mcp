"""
Shopify Brain AI Agent
The thinking brain that reads data, analyzes, and takes actions
Uses Claude API to understand natural language commands and decide what to do
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional
from anthropic import Anthropic
from datetime import datetime

from config.settings import VAULT_PATH, ANTHROPIC_API_KEY
from integrations.shopify.client import shopify_client
from integrations.seo.client import seo_client
from integrations.ga4.client import ga4_client
from integrations.email.service import email_service
from integrations.shopify.actions import ShopifyActions

logger = logging.getLogger(__name__)

class ShopifyBrainAgent:
    """AI Agent that thinks and acts for your Shopify store"""

    def __init__(self, vault_path: Optional[str] = None):
        self.client = Anthropic(api_key=ANTHROPIC_API_KEY)
        self.vault_path = vault_path
        self.vault_context = self._load_vault_context()
        self.actions = ShopifyActions()

        # Tools available to Claude
        self.tools = [
            {
                "name": "get_sales_data",
                "description": "Get sales metrics from Shopify (revenue, orders, AOV)",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "days": {"type": "integer", "description": "Number of days to look back"}
                    }
                }
            },
            {
                "name": "get_inventory",
                "description": "Check inventory levels and low stock items",
                "input_schema": {"type": "object", "properties": {}}
            },
            {
                "name": "get_products",
                "description": "Get list of products from Shopify",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "limit": {"type": "integer", "description": "Max products to return"}
                    }
                }
            },
            {
                "name": "audit_seo",
                "description": "Audit product page SEO health",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "Product URL to audit"}
                    },
                    "required": ["url"]
                }
            },
            {
                "name": "get_traffic",
                "description": "Get website traffic metrics from GA4",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "days": {"type": "integer", "description": "Days to look back"}
                    }
                }
            },
            {
                "name": "update_product",
                "description": "Update product details (title, description, tags, SEO)",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "product_id": {"type": "string", "description": "Product ID"},
                        "updates": {"type": "object", "description": "Fields to update"}
                    },
                    "required": ["product_id", "updates"]
                }
            },
            {
                "name": "draft_blog_post",
                "description": "Draft a blog post about a product or topic",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "topic": {"type": "string", "description": "Blog post topic"},
                        "keywords": {"type": "array", "description": "Target keywords"}
                    },
                    "required": ["topic"]
                }
            },
            {
                "name": "publish_blog",
                "description": "Publish blog post to Shopify",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "content": {"type": "string"},
                        "tags": {"type": "array"}
                    },
                    "required": ["title", "content"]
                }
            },
            {
                "name": "send_report",
                "description": "Send email report to user",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "recipient": {"type": "string", "description": "Email address"},
                        "subject": {"type": "string"},
                        "content": {"type": "string"}
                    },
                    "required": ["recipient", "subject", "content"]
                }
            }
        ]

    def _load_vault_context(self) -> str:
        """Load Obsidian vault context (brand voice, strategy, customer profile)"""
        if not self.vault_path:
            return "No vault configured"
        try:
            vault = Path(self.vault_path)
            if not vault.exists():
                logger.warning(f"Vault path does not exist: {self.vault_path}")
                return "Vault not available"

            # Priority files to always load
            priority_files = [
                "brand-story.md",
                "icp.md",
                "Brand/icp.md",
                "catalog-overview.md",
                "channels.md",
                "competitors.md",
                "Brand/competitors.md",
                "keyword-strategy.md",
                "Marketing/seo/keyword-strategy.md",
                "ad-strategy.md",
                "Marketing/ads/ad-strategy.md",
                "Customers/reviews-insights.md",
                "Customers/support-patterns.md",
                "decision-log.md",
                "Decisions/decision-log.md",
                "experiments.md",
            ]

            sections = []

            # Load priority files first (deduplicated by content)
            seen_content = set()
            for rel_path in priority_files:
                file = vault / rel_path
                if file.exists():
                    content = file.read_text(encoding="utf-8").strip()
                    if content and content not in seen_content:
                        seen_content.add(content)
                        sections.append(f"### {file.stem}\n{content}")

            # Load today's daily note if present
            today = datetime.now().strftime("%Y-%m-%d")
            daily = vault / "Daily" / f"{today}.md"
            if daily.exists():
                content = daily.read_text(encoding="utf-8").strip()
                if content:
                    sections.append(f"### Daily Note ({today})\n{content}")

            if not sections:
                return "Vault found but no readable notes"

            context = "\n\n---\n\n".join(sections)
            logger.info(f"Loaded vault context: {len(sections)} notes, {len(context)} chars")
            return context

        except Exception as e:
            logger.warning(f"Could not load vault: {e}")
            return "Vault not available"

    async def process_command(self, user_command: str) -> Dict[str, Any]:
        """
        Process natural language command using Claude AI
        Claude decides what tools to use and what actions to take
        """
        logger.info(f"Processing command: {user_command}")

        messages = [
            {
                "role": "user",
                "content": f"""You are an AI assistant for a Shopify store. Your job is to help manage the store intelligently.

Store Context:
{self.vault_context}

User Request: {user_command}

Use the available tools to:
1. Understand what the user wants
2. Gather data (sales, inventory, SEO, traffic)
3. Analyze the data
4. Take action (update products, write blogs, send emails)
5. Report back with results

Be proactive - if the user asks to "improve SEO", automatically audit pages, find issues, and make recommendations.
"""
            }
        ]

        # Agentic loop - Claude thinks, calls tools, gets results, thinks again
        max_iterations = 5
        iteration = 0
        final_result = None

        while iteration < max_iterations:
            iteration += 1
            logger.info(f"Iteration {iteration}")

            # Call Claude
            response = self.client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=4096,
                tools=self.tools,
                messages=messages
            )

            logger.info(f"Stop reason: {response.stop_reason}")

            # Check if Claude wants to use tools
            if response.stop_reason == "tool_use":
                # Process tool calls
                tool_results = []

                for content_block in response.content:
                    if content_block.type == "tool_use":
                        tool_name = content_block.name
                        tool_input = content_block.input

                        logger.info(f"Claude calling tool: {tool_name}")
                        logger.info(f"Tool input: {tool_input}")

                        # Execute tool
                        result = await self._execute_tool(tool_name, tool_input)
                        logger.info(f"Tool result: {result}")

                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": content_block.id,
                            "content": json.dumps(result)
                        })

                # Add Claude's response and tool results to conversation
                messages.append({"role": "assistant", "content": response.content})
                messages.append({"role": "user", "content": tool_results})

            elif response.stop_reason == "end_turn":
                # Claude is done thinking - extract final response
                for content_block in response.content:
                    if hasattr(content_block, "text"):
                        final_result = content_block.text
                logger.info("Claude finished processing")
                break

            else:
                logger.warning(f"Unexpected stop reason: {response.stop_reason}")
                break

        return {
            "status": "success",
            "command": user_command,
            "result": final_result or "No result generated",
            "timestamp": datetime.now().isoformat()
        }

    async def _execute_tool(self, tool_name: str, tool_input: Dict) -> Any:
        """Execute the requested tool"""
        try:
            if tool_name == "get_sales_data":
                days = tool_input.get("days", 30)
                data = await shopify_client.get_sales_data(days)
                return {"success": True, "data": data}

            elif tool_name == "get_inventory":
                data = await shopify_client.get_inventory()
                return {"success": True, "data": data}

            elif tool_name == "get_products":
                limit = tool_input.get("limit", 50)
                data = await shopify_client.get_products(limit)
                return {"success": True, "data": data}

            elif tool_name == "audit_seo":
                url = tool_input.get("url")
                data = await seo_client.audit_product_page(url)
                return {"success": True, "data": data}

            elif tool_name == "get_traffic":
                days = tool_input.get("days", 30)
                data = await ga4_client.get_traffic_report(days)
                return {"success": True, "data": data}

            elif tool_name == "update_product":
                product_id = tool_input.get("product_id")
                updates = tool_input.get("updates", {})
                result = await self.actions.update_product(product_id, updates)
                return {"success": True, "data": result}

            elif tool_name == "draft_blog_post":
                topic = tool_input.get("topic")
                keywords = tool_input.get("keywords", [])
                draft = await self.actions.draft_blog_content(topic, keywords)
                return {"success": True, "data": draft}

            elif tool_name == "publish_blog":
                title = tool_input.get("title")
                content = tool_input.get("content")
                tags = tool_input.get("tags", [])
                result = await self.actions.publish_blog(title, content, tags)
                return {"success": True, "data": result}

            elif tool_name == "send_report":
                recipient = tool_input.get("recipient")
                subject = tool_input.get("subject")
                content = tool_input.get("content")
                result = await email_service.send_daily_report(recipient, {
                    "subject": subject,
                    "content": content
                })
                return {"success": result}

            else:
                return {"success": False, "error": f"Unknown tool: {tool_name}"}

        except Exception as e:
            logger.error(f"Tool execution error: {e}")
            return {"success": False, "error": str(e)}


# Initialize agent
agent = ShopifyBrainAgent()


async def run_agent_command(command: str) -> Dict[str, Any]:
    """Simple interface to run agent commands"""
    return await agent.process_command(command)


if __name__ == "__main__":
    # Test the agent
    test_commands = [
        "What's my sales performance this week?",
        "Find products with low SEO and tell me how to improve them",
        "Check inventory and alert me about low stock",
        "Draft a blog post about our best-selling products"
    ]

    async def test():
        for cmd in test_commands[:1]:  # Test one command
            print(f"\n{'='*60}")
            print(f"Command: {cmd}")
            print(f"{'='*60}")
            result = await run_agent_command(cmd)
            print(f"Result: {result['result']}")

    asyncio.run(test())