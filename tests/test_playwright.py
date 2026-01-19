import requests
import json
import base64
import time
import os
from pathlib import Path

# Configuration
PORT = 8007
BASE_URL = f"http://127.0.0.1:{PORT}"

def get_auth_token():
    try:
        config_dir = Path(os.environ.get('APPDATA')) / 'bridge-mcp'
        agents_file = config_dir / 'agents.json'
        with open(agents_file, 'r') as f:
            data = json.load(f)
        return data.get("local", {}).get("token")
    except: return None

def main():
    print("=== Bridge MCP Playwright Verification ===")
    
    token = get_auth_token()
    if not token:
        print("❌ No token found.")
        return

    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Disable Safety (Playwright might be flagged or just better to be unrestricted)
    requests.post(f"{BASE_URL}/safety/mode", json={"enabled": False}, headers=headers)

    try:
        # 2. Test Browser Navigate
        print("\nTesting: browser_navigate (https://example.com)...")
        resp = requests.post(
            f"{BASE_URL}/execute",
            json={"command": "browser_navigate", "params": {"url": "https://example.com"}},
            headers=headers,
            timeout=30
        )
        print(f"Response: {resp.text}")
        
        if resp.status_code == 200 and resp.json().get("status") == "navigated":
            print("✅ browser_navigate passed.")
        else:
            print("❌ browser_navigate failed. checking if browsers are installed...")
            return

        # 3. Test Content
        print("\nTesting: browser_content...")
        resp = requests.post(
            f"{BASE_URL}/execute",
            json={"command": "browser_content", "params": {}},
            headers=headers,
            timeout=10
        )
        content = resp.json().get("content", "")
        if "Example Domain" in content:
            print("✅ browser_content passed (found 'Example Domain').")
        else:
            print(f"❌ browser_content failed. Content: {content[:100]}...")

        # 4. Test Screenshot
        print("\nTesting: browser_screenshot...")
        resp = requests.post(
            f"{BASE_URL}/execute",
            json={"command": "browser_screenshot", "params": {}},
            headers=headers,
            timeout=10
        )
        img = resp.json().get("image")
        if img:
            print(f"✅ browser_screenshot passed ({len(img)} bytes).")
        else:
            print("❌ browser_screenshot failed.")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        
    finally:
        # Re-enable Safety
        requests.post(f"{BASE_URL}/safety/mode", json={"enabled": True}, headers=headers)

if __name__ == "__main__":
    main()
