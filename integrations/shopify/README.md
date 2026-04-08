# Shopify Integration

This folder handles all Shopify API interactions.

## Files

- `client.py` — Shopify API wrapper/client
- `tools.py` — MCP tools for Shopify queries

## What It Provides

**Sales Data:**
- Total sales
- Orders (recent, by date range)
- Revenue metrics

**Product Data:**
- Top-selling products
- Bottom-performing products
- Product catalog
- Product inventory

**Customer Data:**
- Customer count
- Repeat customers
- Customer lifetime value

## Setup

1. Get Shopify API credentials:
   - Go to Shopify Admin > Apps & Integrations > Develop apps
   - Create a private app
   - Get API Key and Password

2. Add to `.env`:
   ```
   SHOPIFY_STORE_URL=your-store.myshopify.com
   SHOPIFY_API_KEY=your_key
   SHOPIFY_API_PASSWORD=your_password
   ```

3. `client.py` will initialize the connection

## MCP Tools (To Be Created)

- `get_sales_report()` — Daily sales summary
- `get_top_products()` — Best-selling products
- `get_bottom_products()` — Underperforming products
- `get_inventory_status()` — Current inventory
- `get_recent_orders()` — Latest orders
