@echo off
title Shopify Brain MCP Setup
echo.
echo  ================================================
echo   Shopify Brain MCP - One Click Setup
echo  ================================================
echo.

:: Check for Node.js
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  [ERROR] Node.js is not installed.
    echo.
    echo  Please install Node.js from: https://nodejs.org
    echo  Download the LTS version, install it, then run this file again.
    echo.
    pause
    exit /b 1
)
echo  [OK] Node.js found.

:: Add firewall rule for Node.js
echo  [..] Configuring firewall...
netsh advfirewall firewall delete rule name="Shopify Brain MCP" >nul 2>&1
netsh advfirewall firewall add rule name="Shopify Brain MCP" dir=out action=allow program="%ProgramFiles%\nodejs\node.exe" enable=yes >nul 2>&1
netsh advfirewall firewall add rule name="Shopify Brain MCP NVM" dir=out action=allow program="%APPDATA%\nvm\v*\node.exe" enable=yes >nul 2>&1
echo  [OK] Firewall configured.

:: Find Claude Desktop config path
set "CONFIG_DIR=%LOCALAPPDATA%\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude"
if not exist "%CONFIG_DIR%" (
    set "CONFIG_DIR=%APPDATA%\Claude"
)
if not exist "%CONFIG_DIR%" (
    mkdir "%CONFIG_DIR%"
)

:: Write Claude Desktop config
echo  [..] Configuring Claude Desktop...
(
echo {
echo   "mcpServers": {
echo     "shopify-brain": {
echo       "command": "npx",
echo       "args": ["-y", "mcp-remote@0.1.0", "http://91.108.122.206:5000/sse", "--allow-http", "--transport", "sse-only"]
echo     }
echo   }
echo }
) > "%CONFIG_DIR%\claude_desktop_config.json"
echo  [OK] Claude Desktop configured.

echo.
echo  ================================================
echo   Setup complete!
echo  ================================================
echo.
echo  Next steps:
echo   1. Restart Claude Desktop (fully quit and reopen)
echo   2. Open a new chat and ask: "How many products do I have?"
echo.
pause
