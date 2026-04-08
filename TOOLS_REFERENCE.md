# Shopify Brain MCP - Tools Reference Guide

**Status:** Phase 2 Complete | 16 Tools Registered | Ready for Testing

---

## 🛍️ Shopify Tools (5 tools)

### 1. `get_sales_report(days=30)`
Get daily sales metrics for your store
- **Returns:** Total orders, revenue, average order value, currency
- **Example:** `get_sales_report(days=7)` → Last week's sales

### 2. `get_inventory_status()`
Check current inventory levels
- **Returns:** Low stock items (<10 units), total locations, inventory count
- **Example:** `get_inventory_status()` → Alert if products running low

### 3. `get_top_products(limit=10)`
Your best-selling products
- **Returns:** Product titles, handles, sales data, inventory
- **Example:** `get_top_products(limit=5)` → Top 5 products this month

### 4. `get_recent_orders(limit=50, status='any')`
Latest customer orders
- **Returns:** Order IDs, customer info, status, totals
- **Statuses:** 'any', 'paid', 'unpaid', 'cancelled', 'pending'
- **Example:** `get_recent_orders(limit=20, status='unpaid')` → Unpaid orders

### 5. `get_order_details(order_id)`
Detailed info for a specific order
- **Returns:** Line items, shipping, customer, payment status
- **Example:** `get_order_details('123456789')` → Full order breakdown

---

## 📊 Google Analytics 4 Tools (5 tools)

### 1. `authenticate_ga4_oauth(auth_code)`
⚠️ **First step** - Authenticate your GA4 account
- **Input:** Authorization code from Google login
- **Returns:** Success/error status
- **How:** User visits your auth link → Google login → Code sent here
- **Example:** `authenticate_ga4_oauth('4/0AX...')` → Saves tokens

### 2. `get_traffic_report(days=30)`
Website traffic analytics
- **Returns:** Active users, sessions, page views, bounce rate
- **Example:** `get_traffic_report(days=30)` → Last 30 days' traffic

### 3. `get_conversion_metrics(days=30)`
Sales conversion data
- **Returns:** Total conversions, conversion rate, purchases, revenue
- **Example:** `get_conversion_metrics(days=7)` → This week's conversions

### 4. `get_user_engagement(days=30)`
How engaged are your visitors?
- **Returns:** Avg session duration, scrolled users, engaged sessions, engagement rate
- **Example:** `get_user_engagement(days=14)` → 2-week engagement metrics

### 5. `get_top_pages(limit=10)`
Your highest-traffic pages
- **Returns:** Page paths with page view counts
- **Example:** `get_top_pages(limit=5)` → Top 5 pages by traffic

---

## 🔍 Ahrefs SEO Tools (4 tools)

### 1. `audit_product_page(product_url)`
SEO health check for any page
- **Returns:** Domain rating, referring domains, backlinks, organic traffic, SEO score
- **Example:** `audit_product_page('https://example.com/product/shoes')` → Full SEO metrics

### 2. `get_keyword_suggestions(keyword)`
Find related keywords to target
- **Returns:** Related keywords with search volume and difficulty
- **Example:** `get_keyword_suggestions('mens running shoes')` → 20 related keywords

### 3. `analyze_competitors(keyword, limit=5)`
See who ranks for your keywords
- **Returns:** Top 5 competitors, their domains, current SERP position, traffic share
- **Example:** `analyze_competitors('athletic shoes', limit=3)` → Top 3 competitors

### 4. `get_seo_recommendations(product_url)`
Actionable optimization tips
- **Returns:** Priority recommendations (high/medium/low) with reasons and impact
- **Example:** `get_seo_recommendations('https://example.com/product')` → How to improve rankings

---

## 📧 Email Tools (2 tools)

### 1. `send_daily_report(recipient, include_products=true, include_traffic=true)`
Email daily performance summary
- **Includes:** Sales, traffic, inventory status in HTML format
- **Example:** `send_daily_report('you@company.com')` → Sends formatted HTML email

### 2. `send_inventory_alert(recipient)`
Alert when items get low on stock
- **Returns:** Success/failure confirmation
- **Recipients:** Can send to multiple emails if called multiple times
- **Example:** `send_inventory_alert('inventory@company.com')` → Low stock notification

---

## 🚀 Quick Start Testing

### Test Shopify Connection
```
get_sales_report(days=7)
→ Should return: sales data for last 7 days
```

### Test GA4 Connection (requires auth first)
```
authenticate_ga4_oauth('YOUR_AUTH_CODE_FROM_GOOGLE')
→ Once successful, then try:
get_traffic_report(days=30)
→ Should return: user sessions, page views, etc.
```

### Test Ahrefs Connection
```
audit_product_page('https://your-store.com/products/example')
→ Should return: domain metrics and SEO score
```

### Test Email Service
```
send_daily_report('your-email@company.com')
→ Should receive HTML formatted email with store metrics
```

---

## 📋 All Tools Summary Table

| Category | Tool | Purpose |
|----------|------|---------|
| 🛍️ **Shopify** | `get_sales_report` | Daily revenue & orders |
| | `get_inventory_status` | Stock levels & alerts |
| | `get_top_products` | Best sellers |
| | `get_recent_orders` | Customer orders |
| | `get_order_details` | Order breakdown |
| 📊 **GA4** | `authenticate_ga4_oauth` | 🔑 Connect Google |
| | `get_traffic_report` | Sessions & users |
| | `get_conversion_metrics` | Sales conversions |
| | `get_user_engagement` | Visitor behavior |
| | `get_top_pages` | Traffic sources |
| 🔍 **Ahrefs** | `audit_product_page` | SEO health |
| | `get_keyword_suggestions` | Keyword research |
| | `analyze_competitors` | Competitor analysis |
| | `get_seo_recommendations` | SEO tips |
| 📧 **Email** | `send_daily_report` | Email summary |
| | `send_inventory_alert` | Stock alerts |

---

## ⚙️ Authentication Status

| Integration | Auth Method | Status |
|-------------|-------------|--------|
| Shopify | API Key:Password | Configured in .env |
| GA4 | OAuth 2.0 | ⏳ Needs `/auth` endpoint |
| Ahrefs | Bearer Token | Configured in .env |
| Email | SMTP | Configured in .env |

---

## 🔧 Next Steps

1. **Test locally** → `python main.py` + MCP Inspector
2. **Build OAuth endpoints** → `/auth` and `/auth/callback`
3. **Deploy to VPS** → Hostinger server setup
4. **Automate reports** → Daily scheduler with APScheduler
5. **Add vault context** → Brand voice integration

---

## 💡 Usage Example Workflow

```
Day 1 - Authenticate
1. Run: authenticate_ga4_oauth('AUTH_CODE')
2. Tokens saved, ready for GA4 calls

Day 2 - Daily Report
1. get_sales_report(days=1)
2. get_traffic_report(days=1)
3. get_inventory_status()
4. send_daily_report('team@company.com')

Day 5 - SEO Audit
1. audit_product_page('https://store.com/product-1')
2. get_seo_recommendations('https://store.com/product-1')
3. analyze_competitors('your-keyword')
4. send_seo_report('marketing@company.com')
```

---

**Ready to test?** → See PHASE_2_COMPLETION.md for test instructions
