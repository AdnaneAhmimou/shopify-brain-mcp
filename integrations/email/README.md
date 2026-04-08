# Email Service Integration

This folder handles email notifications and report delivery.

## Files

- `service.py` — Email service (Gmail, Mailgun, SendGrid)
- `templates/` — Email templates (to be created)

## What It Provides

**Report Delivery:**
- Daily sales reports
- SEO audit reports
- Inventory alerts

**Notifications:**
- Low inventory alerts
- Sales milestones
- System errors

## Setup

### Option 1: Gmail (Recommended)

1. Enable 2-step verification in Google Account
2. Generate app-specific password:
   - Go to Google Account > Security
   - Create app password for "Mail" and "Windows Computer"
3. Add to `.env`:
   ```
   EMAIL_SERVICE=gmail
   EMAIL_FROM=your-email@gmail.com
   EMAIL_PASSWORD=your_app_password
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   ```

### Option 2: Mailgun
```
EMAIL_SERVICE=mailgun
MAILGUN_API_KEY=your_api_key
MAILGUN_DOMAIN=your_domain
```

### Option 3: SendGrid
```
EMAIL_SERVICE=sendgrid
SENDGRID_API_KEY=your_api_key
```

## MCP Tools (To Be Created)

- `send_daily_report(email_to)` — Send daily report via email
- `send_inventory_alert(email_to)` — Send inventory alert
- `send_seo_report(email_to)` — Send SEO audit report
