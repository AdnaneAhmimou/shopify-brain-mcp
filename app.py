"""
Shopify Brain Web Dashboard
Simple interface for users to give commands to the AI Agent
"""

import asyncio
import logging
from flask import Flask, render_template, request, jsonify, redirect
from datetime import datetime

from agent import agent
from integrations.google_auth import get_auth_url, exchange_code, is_authenticated

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False


@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')


@app.route('/api/command', methods=['POST'])
def execute_command():
    """
    Execute a command via the AI Agent
    POST data: {"command": "user's natural language command"}
    """
    try:
        data = request.get_json()
        command = data.get('command', '').strip()

        if not command:
            return jsonify({"error": "No command provided"}), 400

        logger.info(f"Executing command: {command}")

        # Run async agent in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(agent.process_command(command))
        loop.close()

        return jsonify({
            "success": True,
            "command": command,
            "result": result.get('result', 'No result'),
            "timestamp": result.get('timestamp')
        })

    except Exception as e:
        logger.error(f"Error executing command: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/suggestions', methods=['GET'])
def get_suggestions():
    """Get example commands user can try"""
    suggestions = [
        {
            "title": "Sales Performance",
            "examples": [
                "What's my sales performance this week?",
                "Show me revenue for the last 30 days",
                "Which products are best sellers?"
            ]
        },
        {
            "title": "SEO Optimization",
            "examples": [
                "Find products with low SEO and improve them",
                "Audit my product pages for SEO issues",
                "What keywords should I target?",
                "Analyze my competitors"
            ]
        },
        {
            "title": "Inventory Management",
            "examples": [
                "Check inventory levels",
                "Alert me about low stock items",
                "What products are running out?"
            ]
        },
        {
            "title": "Content Creation",
            "examples": [
                "Draft a blog post about our best products",
                "Write SEO-optimized product descriptions",
                "Create marketing copy for new products"
            ]
        },
        {
            "title": "Reports & Analytics",
            "examples": [
                "Give me a daily performance summary",
                "What's my website traffic today?",
                "Show conversion metrics",
                "Get user engagement stats"
            ]
        }
    ]
    return jsonify(suggestions)


@app.route('/api/history', methods=['GET'])
def get_history():
    """Get command history (in memory for now)"""
    # TODO: Implement persistent history storage
    return jsonify([])


@app.route('/auth/google')
def google_auth():
    """Redirect user to Google OAuth consent screen"""
    return redirect(get_auth_url())


@app.route('/auth/google/callback')
def google_callback():
    """Handle Google OAuth callback and save tokens"""
    code = request.args.get('code')
    if not code:
        return jsonify({"error": "No authorization code received"}), 400
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(exchange_code(code))
        loop.close()
        return jsonify({"success": True, "message": "Google account connected! GA4 and Gmail are now active."})
    except Exception as e:
        logger.error(f"Google OAuth error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/auth/status')
def auth_status():
    """Check Google auth status"""
    return jsonify({"google_connected": is_authenticated()})


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok", "timestamp": datetime.now().isoformat()})


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal error: {error}")
    return jsonify({"error": "Internal server error"}), 500


if __name__ == '__main__':
    logger.info("Starting Shopify Brain Dashboard...")
    app.run(debug=False, host='0.0.0.0', port=5000)
