"""
Quick test of the Shopify Brain AI Agent
"""

import sys
import asyncio

# Test 1: Import check
print("=" * 60)
print("TEST 1: Checking imports...")
print("=" * 60)

try:
    print("✓ Importing anthropic...")
    from anthropic import Anthropic
    print("✓ anthropic imported")
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)

try:
    print("✓ Importing flask...")
    from flask import Flask
    print("✓ flask imported")
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)

try:
    print("✓ Importing config...")
    from config.settings import ANTHROPIC_API_KEY, AHREFS_API_KEY, SHOPIFY_STORE_URL
    print(f"✓ config imported")
    print(f"  - ANTHROPIC_API_KEY: {'set' if ANTHROPIC_API_KEY else 'NOT SET'}")
    print(f"  - AHREFS_API_KEY: {'set' if AHREFS_API_KEY else 'NOT SET'}")
    print(f"  - SHOPIFY_STORE_URL: {SHOPIFY_STORE_URL}")
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)

# Test 2: Agent initialization
print("\n" + "=" * 60)
print("TEST 2: Testing Agent initialization...")
print("=" * 60)

try:
    print("✓ Creating ShopifyBrainAgent...")
    from agent import ShopifyBrainAgent
    agent = ShopifyBrainAgent()
    print("✓ Agent created successfully")
    print(f"  - Vault context loaded: {len(agent.vault_context)} chars")
    print(f"  - Tools available: {len(agent.tools)}")
    print(f"  - Tools: {[t['name'] for t in agent.tools]}")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Simple command test
print("\n" + "=" * 60)
print("TEST 3: Testing agent command processing...")
print("=" * 60)

async def test_command():
    try:
        print("✓ Processing command: 'What tools do I have available?'")
        result = await agent.process_command("What tools do I have available?")
        print(f"✓ Command processed")
        print(f"  - Status: {result['status']}")
        print(f"  - Result length: {len(result['result'])} chars")
        print(f"\nAgent Response:\n{result['result'][:500]}...")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

try:
    success = asyncio.run(test_command())
    if not success:
        sys.exit(1)
except Exception as e:
    print(f"✗ Error running async test: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Flask app test
print("\n" + "=" * 60)
print("TEST 4: Testing Flask app...")
print("=" * 60)

try:
    print("✓ Creating Flask app...")
    from app import app
    print("✓ Flask app created")

    with app.test_client() as client:
        print("✓ Testing /health endpoint...")
        response = client.get('/health')
        print(f"  - Status: {response.status_code}")
        print(f"  - Response: {response.get_json()}")

    print("✓ Flask app working")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Summary
print("\n" + "=" * 60)
print("✅ ALL TESTS PASSED!")
print("=" * 60)
print("\nYour Shopify Brain AI Agent is ready to use!")
print("\nTo start the dashboard:")
print("  python app.py")
print("\nThen open: http://localhost:5000")
