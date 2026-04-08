# Deployment to Hostinger VPS

Step-by-step guide to deploy the MCP server to your Hostinger VPS.

## Prerequisites

- Hostinger VPS access (SSH)
- Python 3.9+ installed on VPS
- All API credentials ready in `.env`

## Step 1: Connect to Your VPS

```bash
ssh root@your_vps_ip_address
```

## Step 2: Install Dependencies

```bash
apt-get update
apt-get install -y python3 python3-pip python3-venv git
```

## Step 3: Clone Project to VPS

```bash
cd /home
git clone <your-repo-url> shopify-brain-mcp
cd shopify-brain-mcp
```

Or if not using git, upload via SFTP:
```bash
scp -r shopify-brain-mcp/ root@your_vps_ip:/home/
```

## Step 4: Set Up Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Step 5: Configure Environment

```bash
cp .env.example .env
nano .env
# Edit with your API credentials
```

## Step 6: Test Locally on VPS

```bash
python main.py
# Should show: "MCP Server is running..."
# Press Ctrl+C to stop
```

## Step 7: Set Up Systemd Service (Auto-Start)

Create service file:
```bash
sudo nano /etc/systemd/system/shopify-brain-mcp.service
```

Paste:
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

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable shopify-brain-mcp
sudo systemctl start shopify-brain-mcp
```

Check status:
```bash
sudo systemctl status shopify-brain-mcp
```

## Step 8: Monitor Logs

```bash
tail -f /home/shopify-brain-mcp/logs/mcp-server.log
```

Or with systemd:
```bash
sudo journalctl -u shopify-brain-mcp -f
```

## Step 9: Set Up Firewall (If Needed)

```bash
sudo ufw allow 5000/tcp
```

## Troubleshooting

**Server won't start:**
- Check logs: `tail -f /home/shopify-brain-mcp/logs/mcp-server.log`
- Verify .env is correct
- Test API connections manually

**API connection errors:**
- Verify API credentials
- Check VPS internet connection
- Test API endpoints manually with curl

**Permission errors:**
- Ensure ownership: `sudo chown -R root:root /home/shopify-brain-mcp`
- Check file permissions: `chmod 755 /home/shopify-brain-mcp`

## Next Steps

1. Connect Claude to your MCP server
2. Start using tools in conversations
3. Set up scheduled daily reports (via Claude skill)
