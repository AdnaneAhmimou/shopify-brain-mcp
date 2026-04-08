# Shopify Brain MCP Server

An MCP (Model Context Protocol) server that integrates your Shopify store with Google Analytics 4, SEO tools, and your Shopify Brain vault.

## Project Structure

```
shopify-brain-mcp/
├── config/                 # Configuration & environment setup
├── integrations/
│   ├── shopify/           # Shopify API integration
│   ├── ga4/               # Google Analytics 4 integration
│   ├── seo/               # DataForSEO integration
│   └── email/             # Email service
├── utils/                 # Helper functions & utilities
├── tests/                 # Unit tests
├── main.py                # MCP server entry point
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
└── README.md             # This file
```

## Setup Instructions

### 1. Clone/Create Project Locally
```bash
mkdir shopify-brain-mcp
cd shopify-brain-mcp
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
```bash
cp .env.example .env
# Edit .env with your API credentials
```

### 5. Run MCP Server
```bash
python main.py
```

---

## API Credentials Needed

### Shopify API
- **Where:** Shopify Admin > Apps & Integrations > Develop apps
- **What:** API Key + Password
- **To place in:** `.env` - `SHOPIFY_API_KEY`, `SHOPIFY_API_PASSWORD`

### Google Analytics 4
- **Where:** Google Cloud Console > Service Accounts
- **What:** Service Account JSON file
- **To place in:** `./config/ga4-service-account.json` and `.env` - `GA4_SERVICE_ACCOUNT_JSON_PATH`

### DataForSEO
- **Where:** https://datashape.io/ (free tier available)
- **What:** API Key + Username
- **To place in:** `.env` - `DATASEO_API_KEY`, `DATASEO_API_USERNAME`

### Email Service (Gmail or Mailgun/SendGrid)
- **Gmail:** App-specific password from Google Account
- **Mailgun/SendGrid:** API keys from their dashboards
- **To place in:** `.env` - `EMAIL_SERVICE`, `EMAIL_FROM`, `EMAIL_PASSWORD`

---

## What Each Integration Does

### Shopify Integration
- Fetches: Sales data, products, inventory, orders
- Provides: Top/bottom products, sales metrics, inventory alerts
- Location: `integrations/shopify/`

### GA4 Integration
- Fetches: Traffic, conversion rates, user behavior
- Provides: Traffic metrics, conversion analysis, user segments
- Location: `integrations/ga4/`

### DataForSEO Integration
- Fetches: Product page SEO scores, keyword rankings
- Provides: SEO audit reports, keyword recommendations, optimization suggestions
- Location: `integrations/seo/`

### Email Service
- Sends: Daily reports, alerts, notifications
- Location: `integrations/email/`

---

## Development Workflow

1. **Add credentials to .env**
2. **Test each integration** (see `tests/`)
3. **Run server locally** (`python main.py`)
4. **Deploy to Hostinger VPS** (instructions in DEPLOYMENT.md)

---

## Deployment to Hostinger VPS

See `DEPLOYMENT.md` for step-by-step VPS setup and deployment instructions.

---

## MCP Tools Available (Once Running)

Once the MCP is running, you'll have tools like:
- `get_sales_report` — Daily sales metrics
- `get_traffic_report` — GA4 traffic data
- `audit_products_seo` — SEO audit for products
- `get_top_products` — Best-selling products
- `get_inventory_alerts` — Low stock alerts
- `send_email_report` — Email daily report

---

## Support

For issues, check:
1. `.env` file is set up correctly
2. All API keys are valid
3. Server logs: `./logs/mcp-server.log`
