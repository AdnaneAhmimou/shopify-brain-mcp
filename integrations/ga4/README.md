# Google Analytics 4 Integration

This folder handles all GA4 API interactions.

## Files

- `client.py` — GA4 API wrapper/client
- `tools.py` — MCP tools for GA4 queries

## What It Provides

**Traffic Data:**
- Total sessions
- Users
- Traffic source breakdown
- Page views

**Conversion Data:**
- Conversion rate
- Goal completions
- eCommerce conversions
- Transaction data

**User Behavior:**
- Bounce rate
- Session duration
- User engagement metrics

## Setup

1. Set up Google Analytics 4 Service Account:
   - Go to Google Cloud Console
   - Create a service account
   - Generate JSON key
   - Add service account email to GA4 property as viewer

2. Add to `.env`:
   ```
   GA4_PROPERTY_ID=123456789
   GA4_SERVICE_ACCOUNT_JSON_PATH=./config/ga4-service-account.json
   ```

3. Place `ga4-service-account.json` in `./config/` folder

## MCP Tools (To Be Created)

- `get_traffic_report()` — Traffic metrics
- `get_conversion_report()` — Conversion data
- `get_top_pages()` — Most visited pages
- `get_user_behavior()` — User engagement metrics
