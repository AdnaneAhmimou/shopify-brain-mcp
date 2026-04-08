# Shopify Brain MCP Project - Complete Setup Guide

**Last Updated:** April 7, 2026
**Project Status:** Phase 2 - Implementation
**Tier:** Full Brain

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Current Status](#current-status)
4. [Setup Instructions](#setup-instructions)
5. [Implementation Checklist](#implementation-checklist)
6. [API Integrations](#api-integrations)
7. [Deployment Guide](#deployment-guide)
8. [Testing & Validation](#testing--validation)

---

## 🎯 Project Overview

**Shopify Brain MCP** is a Model Context Protocol (MCP) server that integrates your Shopify store with advanced analytics and SEO tools, using your Shopify Brain vault for intelligent context.

### What It Does

- **Daily Reports:** Sales, traffic, conversion metrics with actionable recommendations
- **Product Audits:** SEO analysis, optimization suggestions, competitor insights
- **Inventory Alerts:** Low stock notifications
- **Performance Analysis:** Traffic sources, top/bottom products, user engagement
- **OAuth Authentication:** Client login for accessing their GA4 data

### Who Uses It

- **You (Store Manager):** Configure, monitor, run daily checks
- **Your Client/Company:** Authenticates with Google to grant GA4 access

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     SHOPIFY BRAIN MCP                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  CLIENT BROWSER                       HOSTINGER VPS              │
│  ┌──────────────┐                   ┌──────────────────────┐   │
│  │              │                   │                      │   │
│  │ Client Login │──OAuth flow───────┤ MCP Server (Python)  │   │
│  │ (via link)   │                   │ :5000                │   │
│  │              │                   │                      │   │
│  └──────────────┘                   ├──────────────────────┤   │
│         ▲                            │ Integrations:        │   │
│         │                            │                      │   │
│         └────────────────────────────┤ • Shopify API        │   │
│              Reports/Data            │ • GA4 (OAuth)        │   │
│                                      │ • Ahrefs SEO         │   │
│      LOCAL MACHINE                   │ • Email Service      │   │
│      ┌──────────────┐                │ • Vault Reader       │   │
│      │              │                │                      │   │
│      │ Shopify      │◄───reads ctx───┤ On VPS:              │   │
│      │ Brain Vault  │                │ /vault/              │   │
│      │ (Obsidian)   │                │                      │   │
│      │              │                └──────────────────────┘   │
│      │ • Brand      │                         ▲                 │
│      │ • Customer   │                         │                 │
│      │ • Strategy   │                    Pulled from:           │
│      │ • Decisions  │                    GitHub repo            │
│      │              │                                            │
│      └──────────────┘                                            │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### Technology Stack

- **Language:** Python 3.9+
- **MCP Framework:** FastMCP
- **Server:** Asyncio (async Python)
- **Transport:** HTTP (Streamable HTTP for VPS)
- **APIs:** REST (Shopify, Ahrefs, GA4, Email)
- **Authentication:** OAuth 2.0 (Google)
- **Deployment:** Hostinger VPS

---

## 📊 Current Status

### Completed (Phase 1)

- [x] Project folder structure created
- [x] Environment configuration template (`.env.example`)
- [x] Config module (`config/settings.py`) - loads environment variables
- [x] Skeleton files for all integrations:
  - [x] `integrations/shopify/` (client + tools)
  - [x] `integrations/ga4/` (client + tools)
  - [x] `integrations/seo/` (client + tools - for Ahrefs)
  - [x] `integrations/email/` (service + tools)
- [x] Main MCP server entry point (`main.py`)
- [x] Requirements.txt with all dependencies
- [x] Documentation (.gitignore, README, DEPLOYMENT.md)
- [x] Shopify Brain vault created and configured

### 🔄 In Progress (Phase 2)

- [ ] Implement Shopify API client methods
- [ ] Implement Ahrefs API client methods
- [ ] Implement GA4 OAuth authentication flow
- [ ] Implement email service (Gmail/SMTP)
- [ ] Register all MCP tools in main server
- [ ] Build OAuth authentication handler for client login

### ⏳ Pending (Phase 3+)

- [ ] Local testing with MCP Inspector
- [ ] Deploy to Hostinger VPS
- [ ] Set up systemd service (auto-restart)
- [ ] Configure GitHub Actions for vault sync
- [ ] Create daily report scheduler
- [ ] Add email report delivery
- [ ] Image generation (Midjourney/alternatives - later phase)

---

## 🚀 Setup Instructions

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- Git (for version control)
- Hostinger VPS access (SSH)
- All API credentials in `.env`

### Step 1: Local Setup

```bash
# Navigate to project
cd ~/Shopify\ Brain/shopify-brain-mcp

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure Environment

```bash
# Copy template and fill in your credentials
cp .env.example .env

# Edit with your credentials
nano .env
```

**Required in `.env`:**
```env
# Shopify
SHOPIFY_STORE=arbasa-7450
SHOPIFY_CLIENT_ID=your_client_id
SHOPIFY_CLIENT_SECRET=your_client_secret
SHOPIFY_API_VERSION=2024-10

# Ahrefs
AHREFS_API_KEY=your_ahrefs_api_key

# GA4 OAuth
GA4_PROPERTY_ID=502804669
GA4_OAUTH_CLIENT_ID=your_client_id
GA4_OAUTH_CLIENT_SECRET=your_client_secret
GA4_OAUTH_REDIRECT_URI=https://srv1534106.hstgr.cloud:5000/auth/callback

# Vault
VAULT_PATH=~/Shopify Brain

# VPS
VPS_DOMAIN=srv1534106.hstgr.cloud
VPS_PORT=5000
```

### Step 3: Test Locally (After Phase 2)

```bash
# Start MCP server
python main.py

# In another terminal, use MCP Inspector
npx @modelcontextprotocol/inspector
```

---

## Implementation Checklist

### Phase 2A: Shopify Integration

- [ ] **Implement `integrations/shopify/client.py`**
  - [ ] `get_sales_data()` - Fetch orders for date range
  - [ ] `get_products()` - Get product list
  - [ ] `get_inventory()` - Get inventory levels
  - [ ] `get_orders()` - Get recent orders
  - [ ] Add error handling and logging

- [ ] **Test Shopify Client**
  - [ ] Verify API authentication
  - [ ] Test each method returns correct data
  - [ ] Check error messages are clear

### Phase 2B: Ahrefs Integration

- [ ] **Implement `integrations/seo/client.py`**
  - [ ] `audit_product_page()` - SEO audit for URL
  - [ ] `get_keyword_suggestions()` - Research keywords
  - [ ] `analyze_competitors()` - Competitor analysis
  - [ ] `get_seo_recommendations()` - Get optimization tips
  - [ ] Add error handling and logging

- [ ] **Test Ahrefs Client**
  - [ ] Verify API authentication
  - [ ] Test each method returns correct data

### Phase 2C: Google Analytics 4 Integration

- [ ] **Implement `integrations/ga4/client.py`**
  - [ ] `authenticate_oauth()` - OAuth token exchange
  - [ ] `get_traffic_report()` - Traffic metrics
  - [ ] `get_conversion_metrics()` - Conversion data
  - [ ] `get_user_engagement()` - Engagement metrics
  - [ ] `get_top_pages()` - Top pages

- [ ] **Implement OAuth Handler**
  - [ ] `/auth` endpoint - Start authentication
  - [ ] `/auth/callback` endpoint - Handle OAuth callback
  - [ ] Token storage and refresh
  - [ ] Secure credential handling

- [ ] **Test GA4 Client**
  - [ ] Verify OAuth flow works
  - [ ] Test data retrieval

### Phase 2D: Email Service

- [ ] **Implement `integrations/email/service.py`**
  - [ ] SMTP connection (Gmail)
  - [ ] `send_daily_report()` - Format and send report
  - [ ] `send_inventory_alert()` - Format and send alert
  - [ ] `send_seo_report()` - Format and send SEO findings
  - [ ] HTML email templates

- [ ] **Test Email Service**
  - [ ] Send test email
  - [ ] Verify formatting

### Phase 2E: MCP Server Setup

- [ ] **Update `main.py`**
  - [ ] Import all tool registration functions
  - [ ] Register Shopify tools
  - [ ] Register GA4 tools
  - [ ] Register Ahrefs tools
  - [ ] Register email tools
  - [ ] Initialize FastMCP server properly

- [ ] **Create `utils/` modules**
  - [ ] `errors.py` - Custom error classes
  - [ ] `formatting.py` - Response formatting
  - [ ] `logging.py` - Logging setup

- [ ] **Test MCP Server**
  - [ ] Server starts without errors
  - [ ] All tools are registered
  - [ ] Tools can be called and return data

---

## 🔌 API Integrations

### Shopify API

**Endpoint:** `https://{API_KEY}:{API_PASSWORD}@{STORE_URL}/admin/api/{VERSION}`

**Required Methods:**
```python
await shopify_client.get_sales_data(days=30)
await shopify_client.get_products(limit=100)
await shopify_client.get_inventory()
await shopify_client.get_orders(limit=50)
```

**Documentation:** [Shopify REST API](https://shopify.dev/api/admin-rest)

---

### Ahrefs API

**Endpoint:** `https://api.ahrefs.com/v3`

**Required Methods:**
```python
await seo_client.audit_product_page(url)
await seo_client.get_keyword_suggestions(keyword)
await seo_client.analyze_competitors(keyword)
await seo_client.get_seo_recommendations(url)
```

**Authentication:** API Key in `Authorization: Bearer {AHREFS_API_KEY}`

**Documentation:** [Ahrefs API](https://ahrefs.com/api/)

---

### Google Analytics 4 API

**Endpoint:** `https://analyticsdata.googleapis.com/v1beta`

**OAuth Flow:**
```
1. Client visits: https://srv1534106.hstgr.cloud:5000/auth
2. Redirected to Google login
3. User grants permission
4. Redirects back to: /auth/callback with code
5. Exchange code for access_token
6. Store token for API calls
```

**Required Methods:**
```python
await ga4_client.authenticate_oauth(auth_code)
await ga4_client.get_traffic_report(days=30)
await ga4_client.get_conversion_metrics(days=30)
await ga4_client.get_user_engagement(days=30)
await ga4_client.get_top_pages(limit=10)
```

**Documentation:** [GA4 Data API](https://developers.google.com/analytics/devguides/reporting/data/v1)

---

### Email Service (SMTP)

**Provider:** Gmail SMTP

**Configuration:**
```
SMTP Server: smtp.gmail.com
Port: 587
TLS: Enabled
Auth: Email + App Password
```

**Required Methods:**
```python
await email_service.send_daily_report(recipient, report_data)
await email_service.send_inventory_alert(recipient, items)
await email_service.send_seo_report(recipient, findings)
```

---

## 📦 Vault Integration

### Vault Location
```
~/Shopify Brain/
├── Brand/
│   ├── tone-of-voice.md      ← Use for report formatting
│   ├── icp.md                ← Use for customer language
│   ├── brand-story.md        ← Use for context
│   └── competitors.md        ← Use for comparison
├── Marketing/
│   ├── channels.md           ← Use for channel selection
│   ├── ads/                  ← Ad strategy context
│   └── seo/                  ← SEO strategy context
└── Analytics/
    ├── experiments.md        ← Ongoing tests
    ├── decisions.md          ← Decision history
    └── weekly-review.md      ← Weekly summaries
```

### How MCP Uses Vault

```python
# Example: Generate daily report using vault context
vault_brand = read_vault("Brand/tone-of-voice.md")
vault_customer = read_vault("Brand/icp.md")

# Fetch data from APIs
shopify_data = await shopify_client.get_sales_data()
ga4_data = await ga4_client.get_traffic_report()

# Format using vault context
report = format_report(
    data=shopify_data + ga4_data,
    brand_voice=vault_brand,
    customer_language=vault_customer
)

# Send via email
await email_service.send_daily_report(recipient, report)
```

---

## 🚀 Deployment Guide

### Step 1: Prepare Hostinger VPS

```bash
# SSH into VPS
ssh root@srv1534106.hstgr.cloud

# Update system
apt-get update && apt-get upgrade -y

# Install Python
apt-get install -y python3 python3-pip python3-venv git
```

### Step 2: Deploy Project

```bash
# Create app directory
mkdir -p /home/shopify-brain-mcp
cd /home/shopify-brain-mcp

# Clone from git (or upload files)
git clone <your-repo-url> .
# OR scp files from local

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Configure Environment

```bash
# Copy .env to VPS
scp .env root@srv1534106.hstgr.cloud:/home/shopify-brain-mcp/

# Or create and edit on VPS
nano .env
```

### Step 4: Set Up Systemd Service

Create `/etc/systemd/system/shopify-brain-mcp.service`:

```ini
[Unit]
Description=Shopify Brain MCP Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/home/shopify-brain-mcp
Environment="PATH=/home/shopify-brain-mcp/venv/bin"
ExecStart=/home/shopify-brain-mcp/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable shopify-brain-mcp
sudo systemctl start shopify-brain-mcp

# Check status
sudo systemctl status shopify-brain-mcp
```

### Step 5: Firewall Rules

```bash
# Allow port 5000
sudo ufw allow 5000/tcp
```

---

## 🧪 Testing & Validation

### Local Testing

```bash
# Terminal 1: Start server
python main.py

# Terminal 2: Test with curl
curl -X GET http://localhost:5000/tools

# Or use MCP Inspector
npx @modelcontextprotocol/inspector
```

### Test Checklist

- [ ] Server starts without errors
- [ ] All tools are registered
- [ ] Shopify tools return data
- [ ] Ahrefs tools return data
- [ ] GA4 OAuth flow works
- [ ] Email sending works
- [ ] Vault is readable

### VPS Testing

```bash
# SSH into VPS
ssh root@srv1534106.hstgr.cloud

# Check server status
sudo systemctl status shopify-brain-mcp

# View logs
sudo journalctl -u shopify-brain-mcp -f

# Test endpoint
curl http://localhost:5000/tools
```

---

## 📅 Timeline

**Phase 2 (This Week):** API Implementation & Testing
- Implement all API clients
- Register all MCP tools
- Local testing

**Phase 3 (Next Week):** VPS Deployment
- Deploy to Hostinger
- Set up systemd service
- Configure firewall

**Phase 4 (Following Week):** Automation & Reporting
- Daily scheduler
- Email reports
- Performance monitoring

---

## 🆘 Troubleshooting

**Server won't start:**
- Check `.env` is configured correctly
- Verify Python version: `python3 --version`
- Check logs: `tail -f logs/mcp-server.log`

**API errors:**
- Verify API keys are correct
- Check API rate limits
- Review error messages in logs

**OAuth not working:**
- Verify redirect URI in Google Cloud matches `.env`
- Check token storage permissions
- Review OAuth logs

---

## 📚 Additional Resources

- [FastMCP Documentation](https://github.com/modelcontextprotocol/python-sdk)
- [Shopify REST API](https://shopify.dev/api)
- [Ahrefs API Docs](https://ahrefs.com/api/)
- [GA4 Data API](https://developers.google.com/analytics)
- [OAuth 2.0 Flow](https://tools.ietf.org/html/rfc6749)

---

## 📝 Notes

- Images (Midjourney/DALL-E) - To be implemented in Phase 4
- Scheduled reports - To be implemented with APScheduler
- Database - Currently using file-based storage, consider PostgreSQL for scale

---

**Questions?** Check the README.md or DEPLOYMENT.md files for more details.
