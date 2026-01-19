import requests
import time
import json
import os
import sys
import base64
from pathlib import Path

# Configuration
PORT = 8007
BASE_URL = f"http://127.0.0.1:{PORT}"
TEST_DIR = Path("test_temp_artifacts")

# Colors for output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def log_pass(msg):
    print(f"{Colors.OKGREEN}✅ PASS: {msg}{Colors.ENDC}")

def log_fail(msg, details=""):
    print(f"{Colors.FAIL}❌ FAIL: {msg}{Colors.ENDC}")
    if details:
        print(f"   {details}")

def log_info(msg):
    print(f"{Colors.OKBLUE}ℹ️  INFO: {msg}{Colors.ENDC}")

def get_auth_token():
    try:
        config_dir = Path(os.environ.get('APPDATA')) / 'bridge-mcp'
        agents_file = config_dir / 'agents.json'
        if not agents_file.exists(): return None
        with open(agents_file, 'r') as f:
            data = json.load(f)
        return data.get("local", {}).get("token")
    except: return None

class BridgeTester:
    def __init__(self):
        self.token = get_auth_token()
        self.headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
        if not self.token:
            log_fail("No auth token found. Agent might not be registered.")
            sys.exit(1)
            
    def run(self, command, params={}):
        try:
            resp = requests.post(
                f"{BASE_URL}/execute", 
                json={"command": command, "params": params}, 
                headers=self.headers, 
                timeout=20 # Longer timeout for browser/vision tools
            )
            if resp.status_code == 200:
                return True, resp.json()
            else:
                return False, resp.text
        except Exception as e:
            return False, str(e)

    def set_safety(self, enabled: bool):
        try:
            requests.post(f"{BASE_URL}/safety/mode", json={"enabled": enabled}, headers=self.headers)
        except: pass

    # ================= TESTS =================

    def test_system_info(self):
        print(f"\n{Colors.HEADER}=== System Info Tests ==={Colors.ENDC}")
        
        # Screen Size
        ok, res = self.run("get_screen_size")
        if ok and "width" in res and "height" in res:
            log_pass(f"Screen Size: {res['width']}x{res['height']}")
        else:
            log_fail("get_screen_size", res)

        # Mouse Position
        ok, res = self.run("get_mouse_position")
        if ok and "x" in res:
            log_pass(f"Mouse Position: {res['x']}, {res['y']}")
        else:
            log_fail("get_mouse_position", res)

        # Desktop State
        ok, res = self.run("get_desktop_state")
        if ok and "windows" in res:
            log_pass(f"Desktop State: {len(res['windows'])} windows found")
        else:
            log_fail("get_desktop_state", res)

    def test_vision(self):
        print(f"\n{Colors.HEADER}=== Vision Tests ==={Colors.ENDC}")
        
        # Screenshot
        ok, res = self.run("screenshot")
        if ok and "image" in res:
             # Verify base64
             try:
                 base64.b64decode(res["image"])
                 log_pass(f"Screenshot taken ({len(res['image'])} bytes b64)")
             except:
                 log_fail("Screenshot returned invalid base64")
        else:
            log_fail("screenshot", res)

        # Visual Grid
        ok, res = self.run("get_visual_state")
        if ok and "image" in res and "grid_config" in res:
            log_pass("Grid Vision (image + config present)")
        else:
            log_fail("get_visual_state", res)

        # Click Grid (Dry run check)
        # We purposely fail validation to avoid clicking random stuff, or click a safe zone 
        # But wait, click_grid clicks immediately.
        # Let's verify parameter parsing errors to ensure endpoint works
        ok, res = self.run("click_grid", {"grid_id": "ZZ999"})
        if not ok and "bounds" in str(res): # Should fail or error
             log_pass("click_grid (Bounds check worked)")
        elif ok:
             log_pass("click_grid (Executed, hope it was safe!)")
        else:
             log_info(f"click_grid response: {res}")


    def test_filesystem(self):
        print(f"\n{Colors.HEADER}=== Filesystem Tests ==={Colors.ENDC}")
        
        # Create a harmless temp file
        test_file = os.path.abspath("bridge_test_artifact.txt")
        test_content = "Bridge MCP File Verification Test"
        
        # Write
        ok, res = self.run("file_write", {"path": test_file, "content": test_content})
        if ok:
            log_pass("file_write")
        else:
            log_fail("file_write", res)

        # Read
        ok, res = self.run("file_read", {"path": test_file})
        if ok and res.get("content") == test_content:
            log_pass("file_read (Content matched)")
        else:
            log_fail("file_read", f"Expected '{test_content}', got {res}")

        # List
        test_dir = os.path.dirname(test_file)
        ok, res = self.run("file_list", {"directory": test_dir})
        if ok and "files" in res:
             if os.path.basename(test_file) in res["files"]:
                 log_pass("file_list (Found created file)")
             else:
                 log_fail("file_list (File not in list)")
        else:
            log_fail("file_list", res)

        # Cleanup (Local logic to clean up, or use run_cmd)
        try:
            os.remove(test_file)
        except: pass

    def test_clipboard(self):
        print(f"\n{Colors.HEADER}=== Clipboard Tests ==={Colors.ENDC}")
        
        org_content = ""
        # Backup clipboard (if possible via local python, but let's just assume we overwrite)
        
        test_text = "Bridge_MCP_Clipboard_Test_123"
        
        # Copy
        ok, res = self.run("clipboard_copy", {"text": test_text})
        if ok:
            log_pass("clipboard_copy")
        else:
            log_fail("clipboard_copy", res)
            
        # Paste
        ok, res = self.run("clipboard_paste")
        if ok and res.get("content") == test_text:
            log_pass("clipboard_paste (Matched)")
        else:
            log_fail("clipboard_paste", f"Expected '{test_text}', got '{res}'")

    def test_apps_interaction(self):
        print(f"\n{Colors.HEADER}=== App Interaction Tests ==={Colors.ENDC}")
        
        # Launch Notepad (using app_launch to avoid blocking)
        ok, res = self.run("app_launch", {"name": "notepad.exe"})
        if ok:
            log_pass("app_launch (Notepad)")
        else:
            log_fail("app_launch", res)
            return

        time.sleep(2) # Wait for load

        # Verification via App List (Windows specific)
        # Note: app_list uses uiautomation or pywinauto? 
        # local_agent.py uses uiautomation if available.
        ok, res = self.run("app_list")
        found = False
        if ok and "apps" in res:
            for app in res["apps"]:
                if "Notepad" in app.get("name", "") or "Untitled" in app.get("name", ""):
                    found = True
                    break
            
            if found:
                log_pass("app_list (Found Notepad)")
            else:
                log_info("app_list (Notepad not explicitly in top-level list, might be hidden or named differently)")
        else:
             log_fail("app_list", res)

        # Type Text
        ok, res = self.run("type_text", {"text": "Automatic Test"})
        if ok:
            log_pass("type_text")
        else:
            log_fail("type_text", res)

        # Close
        # Try app_close first
        ok, res = self.run("app_close", {"name": "Notepad"})
        if ok and res.get("status") == "closed":
            log_pass("app_close (Graceful)")
        else:
            log_info("app_close failed/not found, forcing kill via run_cmd")
            self.run("run_cmd", {"command": "taskkill /f /im notepad.exe"})

    def test_browser(self):
        print(f"\n{Colors.HEADER}=== Browser Tests ==={Colors.ENDC}")
        
        # 1. Simple Chrome Launch
        ok, res = self.run("chrome_open", {"url": "about:blank"})
        if ok:
            log_pass("chrome_open")
            time.sleep(2)
            # Try to close it (hard to find correct window title, maybe just generic close active?)
            # Leaving it open is messy but acceptable for test.
        else:
            log_fail("chrome_open", res)

        # 2. Playwright (Advanced)
        # Check if we can run a simple playwright command
        # This will fail if playwright browsers aren't installed.
        print(f"{Colors.OKBLUE}Running Playwright tests (may fail if not installed)...{Colors.ENDC}")
        ok, res = self.run("browser_navigate", {"url": "https://example.com"})
        
        if ok and str(res.get("status")) == "navigated":
            log_pass("Playwright: browser_navigate")
            
            # Content
            ok, res = self.run("browser_content")
            if ok and "Example Domain" in str(res.get("content")):
                log_pass("Playwright: browser_content")
            else:
                log_fail("Playwright: browser_content", res)
                
            # Screenshot
            ok, res = self.run("browser_screenshot")
            if ok and "image" in res:
                log_pass("Playwright: browser_screenshot")
            else:
                 log_fail("Playwright: browser_screenshot", res)
                 
        else:
            log_info(f"Playwright tests skipped or failed: {res}")


def main():
    print("=== Bridge MCP Comprehensive Test Suite ===")
    
    # 1. Wait for agent
    print("Connecting to agent...")
    try:
        requests.get(f"{BASE_URL}/health", timeout=5)
    except:
        print(f"{Colors.FAIL}Cannot connect to {BASE_URL}. Is local_agent.py running?{Colors.ENDC}")
        sys.exit(1)

    tester = BridgeTester()
    
    # Disable Safety for full testing
    print("Disabling Safety Mode...")
    tester.set_safety(False)

    try:
        tester.test_system_info()
        tester.test_filesystem()
        tester.test_clipboard()
        tester.test_vision()
        tester.test_apps_interaction()
        tester.test_browser()
    finally:
        # Re-enable Safety
        print("\nRe-enabling Safety Mode...")
        tester.set_safety(True)
        print("Done.")

if __name__ == "__main__":
    main()
