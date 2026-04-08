# Shopify Brain AI Agent - Setup Guide

## What We Just Built

You now have a **complete AI Agent** that:

1. **Listens** to your commands in natural language
2. **Thinks** using Claude AI to understand what you want
3. **Acts** by calling the right tools (Shopify, Ahrefs, GA4, Email)
4. **Decides** what changes to make automatically
5. **Reports** back with results

---

## 🚀 Quick Start (5 minutes)

### Step 1: Add Claude API Key

Get your API key from: https://console.anthropic.com/

Add to your `.env` file:

```env
ANTHROPIC_API_KEY=sk-ant-v0-xxx...
```

### Step 2: Install New Dependencies

```bash
cd ~/Shopify\ Brain/shopify-brain-mcp
pip install -r requirements.txt
```

New packages installed:
- `anthropic==0.31.0` - Claude API client
- `flask==3.0.0` - Web framework
- `flask-cors==4.0.0` - Cross-origin support

### Step 3: Start the Agent Dashboard

```bash
python app.py
```

You should see:
```
* Running on http://0.0.0.0:5000
```

### Step 4: Open in Browser

Go to: **http://localhost:5000**

You'll see a clean interface where you can type commands.

---

## 💬 Example Commands to Try

### Sales & Revenue
```
What's my sales performance this week?
Show me revenue for the last 30 days
Which products are best sellers?
```

### SEO & Content
```
Find products with low SEO and improve them
Audit my product pages for SEO issues
Draft a blog post about our best-selling products
```

### Inventory
```
Check inventory levels
Alert me about low stock items
What products are running out?
```

### Full Automation Examples
```
"Find the 5 products with lowest SEO scores, improve their titles and descriptions, draft a blog post about them, and send me a summary"
```

When you send this command, the agent will:
1. Get all products
2. Audit each for SEO
3. Find the 5 worst
4. Generate better titles/descriptions
5. Draft blog content
6. Send you an email summary
7. Report back with results

---

## 🧠 How the Agent Works

### 1. You Give a Command
```
"Find low SEO products and improve them"
```

### 2. Agent Thinks (Claude AI)
- Understands your request
- Makes a plan
- Decides which tools to use
- Reads your brand voice from vault (if set up)

### 3. Agent Acts
- Calls `get_products()` → Gets all products
- Calls `audit_page()` on each → Gets SEO scores
- Analyzes results → "These 5 need help"
- Calls `update_product()` → Updates titles/descriptions
- Calls `draft_blog_post()` → Writes content
- Calls `send_email()` → Sends you report

### 4. You Get Results
```
Found 5 products with low SEO
Updated 5 product titles and descriptions
Drafted 2 blog posts
Email sent with summary
```

---

## 📁 New Files Created

```
agent.py                          ← The AI brain (Claude + orchestration)
integrations/shopify/actions.py   ← Write operations (update products, etc)
app.py                            ← Web dashboard (Flask)
templates/index.html              ← Beautiful web interface
```

---

## ⚙️ Configuration

The agent reads from your `.env` file:

```env
# Existing (already configured)
SHOPIFY_STORE_URL=...
SHOPIFY_API_KEY=...
AHREFS_API_KEY=...
GA4_PROPERTY_ID=...
EMAIL_FROM=...

# NEW - Add this
ANTHROPIC_API_KEY=sk-ant-v0-xxx...
```

---

## 🔄 Agent Architecture

```
┌─────────────────────────────────────────────────────┐
│             Web Dashboard (Flask)                   │
│  Clean interface where users type commands         │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────┐
│          AI Agent (agent.py)                        │
│  • Claude API - Thinks and makes decisions         │
│  • Understands natural language                     │
│  • Makes a plan                                     │
│  • Calls tools in right order                       │
└──────────────────┬──────────────────────────────────┘
                   │
        ┌──────────┼──────────┐
        │          │          │
        ▼          ▼          ▼
     ┌──────┐ ┌──────────┐ ┌──────────┐
     │Read  │ │Action    │ │Analytics │
     │      │ │Methods   │ │          │
     │Tools │ │(Write)   │ │(Ahrefs,  │
     │      │ │          │ │GA4)      │
     └──────┘ └──────────┘ └──────────┘
        │          │          │
        └──────────┼──────────┘
                   │
        ┌──────────┼──────────┐
        │          │          │
        ▼          ▼          ▼
   ┌─────────┐ ┌──────────┐ ┌──────────┐
   │Shopify  │ │Email     │ │Ahrefs/GA4│
   │API      │ │Service   │ │APIs      │
   └─────────┘ └──────────┘ └──────────┘
```

---

## 🧪 Testing

### Test 1: Check Dashboard Loads
```
Open: http://localhost:5000
You should see a beautiful purple interface
```

### Test 2: Simple Command
```
Type: "What's my sales for this week?"
Click: Send
Expected: Sales data appears below
```

### Test 3: Complex Command
```
Type: "Find products with low SEO and tell me how to improve them"
Click: Send
Expected: Agent analyzes products, gives recommendations
```

### Test 4: Action Command
```
Type: "Update my product descriptions for better SEO"
Click: Send
Expected: Agent updates products, confirms changes
```

---

## 🚀 What's Next

### Phase 1: Local Testing (You are here)
- [x] Build AI Agent
- [x] Create web dashboard
- [x] Test commands locally
- [ ] Verify all API connections work

### Phase 2: Automation (Next)
- [ ] Set up daily scheduler
- [ ] Automated morning reports
- [ ] Scheduled SEO audits
- [ ] Automatic blog drafting

### Phase 3: VPS Deployment
- [ ] Deploy to Hostinger
- [ ] Set up systemd service
- [ ] Enable 24/7 operation
- [ ] Real-time notifications

---

## ⚠️ Troubleshooting

### Error: "ModuleNotFoundError: No module named 'anthropic'"
**Solution:** Run `pip install anthropic`

### Error: "ANTHROPIC_API_KEY not found"
**Solution:** Add to .env file and restart app

### Error: "Connection to Shopify failed"
**Solution:** Check Shopify credentials in .env

### Dashboard loads but commands don't work
**Solution:** Check browser console (F12) for errors, check app.py logs

---

## 📚 Learn More

- **Claude API Docs:** https://docs.anthropic.com
- **Shopify API:** https://shopify.dev/api
- **Ahrefs API:** https://ahrefs.com/api
- **GA4 API:** https://developers.google.com/analytics/devguides

---

## 🎯 Ready to Go?

1. **Update `.env`** with `ANTHROPIC_API_KEY`
2. **Install dependencies:** `pip install -r requirements.txt`
3. **Start dashboard:** `python app.py`
4. **Open browser:** `http://localhost:5000`
5. **Give it a command!**

The AI will handle the rest. No technical knowledge needed from your client.

---

**Questions?** The system will learn from your feedback and improve over time.
