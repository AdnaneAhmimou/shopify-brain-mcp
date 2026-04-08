# ⚡ Quick Start - Shopify Brain Agent

## Status Overview
✅ **Obsidian Vault:** Connected  
❌ **Shopify API:** Needs credential fix  
⚠️ **Google Analytics 4:** Needs OAuth setup  
✅ **AI Agent:** Ready to run  

---

## 🚀 Start the Web Dashboard (Recommended)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt --break-system-packages
```

### Step 2: Start the Flask App
```bash
python app.py
```

You should see:
```
* Running on http://0.0.0.0:5000
```

### Step 3: Open in Browser
Go to: **http://localhost:5000**

You'll see a clean interface to send commands to the agent.

---

## 🧪 Quick Test Commands

Once running, try these commands:

### Test 1: Check Vault Connection
```
"What's in my Shopify Brain vault?"
```
Expected: Agent reads vault files and summarizes them

### Test 2: Check Shopify Data (Once Fixed)
```
"Show me my products"
```
Expected: Lists products from your Shopify store

### Test 3: Check GA4 Data (Once OAuth is set up)
```
"What's my traffic this week?"
```
Expected: Shows website traffic metrics

---

## 🔧 Fix Shopify Authentication

**Error:** `403 Forbidden`

**Solution:**
1. Go to your Shopify Admin
2. Navigate to: **Settings** → **Apps and integrations** → **Develop apps**
3. Find the app and click **Configuration**
4. In **Admin API credentials** section:
   - Click **Reveal** on API Key and API Password
   - Copy both values
5. Update your `.env` file:
   ```env
   SHOPIFY_API_KEY=<new_key>
   SHOPIFY_API_PASSWORD=<new_password>
   ```
6. Save and restart the app

---

## 🔐 Setup GA4 OAuth

**When it happens:** First time you ask an analytics question

**What to do:**
1. The agent will generate an OAuth login link
2. Click the link to authorize Google Analytics
3. Grant permissions for your GA4 property
4. The agent will save the token automatically

---

## 📚 File Structure

```
shopify-brain-mcp/
├── app.py                    ← Web dashboard (Flask)
├── agent.py                  ← AI brain (Claude)
├── main.py                   ← MCP server entry
│
├── integrations/
│   ├── shopify/             ← Shopify API
│   ├── ga4/                 ← Google Analytics
│   ├── seo/                 ← SEO tools
│   └── email/               ← Email notifications
│
├── config/
│   └── settings.py          ← Configuration
│
├── templates/
│   └── index.html           ← Web interface
│
└── logs/
    └── mcp-server.log       ← Debug logs
```

---

## 🎯 What the Agent Can Do

### Today (Working)
- ✅ Read Obsidian vault notes
- ✅ Understand natural language commands
- ✅ Draft content (blog posts, emails)
- ✅ Analyze data from vault

### After Fixes
- 🔧 Fetch Shopify sales & inventory data
- 🔧 Pull Google Analytics traffic metrics
- 🔧 Audit SEO scores of product pages
- 🔧 Send automated reports
- 🔧 Update product information

---

## 📊 Example: Full Automation Flow

**You command:**
```
"Find my 3 best-selling products and create a blog post about them"
```

**Agent does:**
1. Reads Shopify data → finds top 3 products
2. Checks your brand voice from vault
3. Researches SEO keywords
4. Drafts a blog post
5. Saves it to vault for review
6. Sends you summary email

---

## 🐛 Troubleshooting

### Dashboard won't start
```bash
# Check if port 5000 is free
lsof -i :5000

# If busy, kill it or use different port
python app.py --port 5001
```

### Agent doesn't respond
```bash
# Check logs
tail -f logs/mcp-server.log

# Verify .env file exists and has all keys
cat .env | grep -E "ANTHROPIC|SHOPIFY|GA4"
```

### Shopify returns 403
- Verify API credentials are current
- Check app has required scopes
- Regenerate tokens if > 30 days old

### GA4 returns "Not authenticated"
- GA4 uses OAuth, which requires browser login
- First analytics command will trigger auth flow
- Follow the OAuth login prompt

---

## 🎓 Example Commands to Try

```
# Simple data queries
"What products do I have?"
"Show inventory status"
"What's in my vault?"

# Analysis
"Which products need SEO work?"
"Analyze my customer segments"
"Compare sales by channel"

# Actions
"Draft a product description for [product name]"
"Create a blog post about [topic]"
"Send me a daily sales report"

# Complex automation
"Identify low-performing products, draft content improvements, and email me a summary"
"Check inventory, find items under 5 units, and update the vault"
```

---

## 📞 Need Help?

Check these files:
- **Setup issues:** AGENT_SETUP.md
- **Integration errors:** INTEGRATION_TEST_REPORT.md
- **Deployment:** DEPLOYMENT.md
- **API reference:** TOOLS_REFERENCE.md

---

**Last Updated:** 2026-04-07  
**Status:** Ready to run (pending Shopify auth fix)
