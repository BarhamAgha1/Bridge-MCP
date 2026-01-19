import requests
import time
import json
import os
import sys
from pathlib import Path

# Configuration
PORT = 8007
BASE_URL = f"http://127.0.0.1:{PORT}"

def get_auth_token():
    """Retrieve the auth token from the persistent storage."""
    try:
        config_dir = Path(os.environ.get('APPDATA')) / 'bridge-mcp'
        agents_file = config_dir / 'agents.json'
        
        if not agents_file.exists():
            print(f"Error: agents.json not found at {agents_file}")
            return None
            
        with open(agents_file, 'r') as f:
            data = json.load(f)
            
        token = data.get("local", {}).get("token")
        if not token:
            print("Error: No token found for 'local' agent in agents.json")
        else:
             print(f"Found token involved: {token[:4]}...")
        return token
    except Exception as e:
        print(f"Error reading token: {e}")
        return None

def test_connectivity():
    """Check if agent is reachable."""
    try:
        print(f"Checking health at {BASE_URL}/health...")
        resp = requests.get(f"{BASE_URL}/health", timeout=5)
        if resp.status_code == 200:
            print("✅ Agent is healthy!")
            return True
        else:
            print(f"❌ Agent returned status {resp.status_code}")
            print(resp.text)
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to agent. Is it running?")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def run_command(command, params, token):
    """Execute a command on the agent."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "command": command,
        "params": params
    }
    
    try:
        print(f"Running command '{command}'...")
        resp = requests.post(f"{BASE_URL}/execute", json=payload, headers=headers, timeout=10)
        
        if resp.status_code == 200:
            result = resp.json()
            print(f"✅ Success: {json.dumps(result)[:100]}...") # Truncate output
            return True
        elif resp.status_code == 403:
             print(f"⚠️ Blocked (Expected for unsafe commands without approval): {resp.text}")
             return True # This is a pass for safety tests
        else:
            print(f"❌ Failed: {resp.status_code} - {resp.text}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def main():
    print("=== Bridge MCP E2E Test ===")
    
    # 1. Wait for agent to start
    retries = 5
    while retries > 0:
        if test_connectivity():
            break
        print("Waiting for agent to start...")
        time.sleep(2)
        retries -= 1
    
    if retries == 0:
        print("❌ Timed out waiting for agent.")
        sys.exit(1)

    # 2. Get Token
    token = get_auth_token()
    if not token:
        print("❌ Cannot proceed without token.")
        sys.exit(1)

    # --- DISABLE SAFETY FIRST ---
    print("\n--- Disabling Safety Mode for Testing ---")
    headers = {"Authorization": f"Bearer {token}"}
    try:
        resp = requests.post(f"{BASE_URL}/safety/mode", json={"enabled": False}, headers=headers)
        if resp.status_code == 200:
            print("✅ Safety Disabled")
        else:
            print(f"❌ Failed to disable safety: {resp.text}")
    except Exception as e:
        print(f"❌ Error disabling safety: {e}")
        # Proceeding might fail, but let's try

    # 3. Test Read-Only Tools
    print("\n--- Testing Read-Only Tools ---")
    if not run_command("get_screen_size", {}, token):
        pass # Don't exit, try others
    
    if not run_command("get_mouse_position", {}, token):
        pass

    # 4. Test Interaction (Notepad)
    print("\n--- Testing Interaction (Notepad) ---")
    # Launch Notepad using app_launch (returns immediately)
    if run_command("app_launch", {"name": "notepad.exe"}, token):
        # Wait for it to open
        time.sleep(2)
        
        # Type something
        run_command("type_text", {"text": "Hello form Bridge Test"}, token)
        
        # Close Notepad (Force kill to avoid save prompt)
        time.sleep(1)
        run_command("run_cmd", {"command": "taskkill /f /im notepad.exe"}, token)

    # 5. Test Safety Sentinel (Re-enable)
    print("\n--- Re-enabling Safety ---")
    try:
        requests.post(f"{BASE_URL}/safety/mode", json={"enabled": True}, headers=headers)
        print("✅ Safety Re-enabled")
    except Exception as e:
        print(f"❌ Error enabling safety: {e}")

    # Test Safety Block
    print("\n--- Testing Safety Block (Should Timeout/Block) ---")
    try:
        # We expect a timeout because the agent will block waiting for UI approval
        print("Running dangerous command (expecting block)...")
        resp = requests.post(
            f"{BASE_URL}/execute", 
            json={"command": "run_powershell", "params": {"command": "echo bad"}}, 
            headers=headers, 
            timeout=3
        )
        if resp.status_code == 403:
            print("✅ Blocked as expected (403).")
        else:
            print(f"⚠️ Warning: Request returned {resp.status_code} (Expected 403 or Timeout)")
            print(resp.text)
    except requests.exceptions.Timeout:
        print("✅ Blocked as expected (Timeout waiting for approval).")
    except Exception as e:
        print(f"❌ Unexpected error during safety test: {e}")

    print("\n=== All Tests Completed ===")

if __name__ == "__main__":
    main()
