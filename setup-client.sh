#!/bin/bash

echo ""
echo " ================================================"
echo "  Shopify Brain MCP - One Click Setup (Mac)"
echo " ================================================"
echo ""

# Check for Node.js
if ! command -v node &> /dev/null; then
    echo " [ERROR] Node.js is not installed."
    echo ""
    echo " Please install Node.js from: https://nodejs.org"
    echo " Download the LTS version, install it, then run this script again."
    echo ""
    exit 1
fi
echo " [OK] Node.js found: $(node --version)"

# Find Claude Desktop config path
CONFIG_DIR="$HOME/Library/Application Support/Claude"
if [ ! -d "$CONFIG_DIR" ]; then
    mkdir -p "$CONFIG_DIR"
fi

# Write Claude Desktop config
echo " [..] Configuring Claude Desktop..."
cat > "$CONFIG_DIR/claude_desktop_config.json" << 'EOF'
{
  "mcpServers": {
    "shopify-brain": {
      "command": "npx",
      "args": ["-y", "mcp-remote@latest", "http://91.108.122.206:5000/sse", "--allow-http", "--transport", "sse-only"]
    }
  }
}
EOF
echo " [OK] Claude Desktop configured."

echo ""
echo " ================================================"
echo "  Setup complete!"
echo " ================================================"
echo ""
echo " Next steps:"
echo "  1. Restart Claude Desktop (fully quit and reopen)"
echo "  2. Open a new chat and ask: 'How many products do I have?'"
echo ""
