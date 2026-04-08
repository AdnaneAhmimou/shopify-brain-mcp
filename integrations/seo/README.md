# DataForSEO Integration

This folder handles SEO analysis and optimization recommendations.

## Files

- `client.py` — DataForSEO API wrapper/client
- `tools.py` — MCP tools for SEO queries

## What It Provides

**SEO Audits:**
- Product page SEO scores
- Title/description analysis
- Keyword recommendations
- Technical SEO issues

**Competitive Analysis:**
- Competitor keyword rankings
- Backlink analysis
- Content gaps

**Keyword Research:**
- Search volume
- Difficulty scores
- Related keywords
- Trending keywords

## Setup

1. Sign up for DataForSEO:
   - Go to https://datashape.io/
   - Create free account (free tier available)
   - Get API Key

2. Add to `.env`:
   ```
   DATASEO_API_KEY=your_api_key
   DATASEO_API_USERNAME=your_username
   ```

## MCP Tools (To Be Created)

- `audit_product_page(product_url)` — SEO audit for a product
- `suggest_keywords(product_name)` — Keyword suggestions
- `analyze_competitors(keyword)` — Competitor analysis
- `bulk_audit_products()` — Audit all products
- `get_seo_recommendations()` — Top optimization suggestions
