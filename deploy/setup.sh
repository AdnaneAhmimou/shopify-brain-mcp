#!/bin/bash
# Shopify Brain MCP — VPS Setup Script
# Run as root on Hostinger VPS: bash setup.sh

set -e

echo "=== Shopify Brain MCP Setup ==="

# Install Python if needed
apt-get update -qq
apt-get install -y python3 python3-pip python3-venv git

# Create virtualenv
cd /root/shopify-brain-mcp
python3 -m venv venv
venv/bin/pip install --upgrade pip
venv/bin/pip install -r requirements.txt

# Create logs and tokens directories
mkdir -p logs tokens

# Install systemd services
cp deploy/shopify-brain-mcp.service /etc/systemd/system/
cp deploy/shopify-brain-auth.service /etc/systemd/system/
systemctl daemon-reload

# Enable and start services
systemctl enable shopify-brain-mcp
systemctl enable shopify-brain-auth
systemctl start shopify-brain-mcp
systemctl start shopify-brain-auth

# Open firewall ports
ufw allow 5000/tcp  # MCP SSE
ufw allow 5001/tcp  # Auth server

echo ""
echo "=== Setup Complete ==="
echo "MCP server:  http://$(hostname -I | awk '{print $1}'):5000/sse"
echo "Auth server: http://$(hostname -I | awk '{print $1}'):5001"
echo ""
echo "Check status:"
echo "  systemctl status shopify-brain-mcp"
echo "  systemctl status shopify-brain-auth"
echo ""
echo "View logs:"
echo "  tail -f /root/shopify-brain-mcp/logs/mcp-server.log"
