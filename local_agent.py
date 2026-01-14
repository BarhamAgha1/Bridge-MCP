"""
Bridge MCP - Local Agent
========================
This runs on your Windows PC and executes commands from the cloud relay.

Requirements: pip install -r requirements-local.txt
Usage: python local_agent.py
"""

import asyncio
import json
import base64
import subprocess
from io import BytesIO
from typing import Optional
from aiohttp import web
import socket

# Auth Token
AUTH_TOKEN = None

async def auto_register_with_bridge():
    """
    Automatically register this agent with the Bridge MCP config file.
    This ensures persistence across sessions.
    """
    global AUTH_TOKEN
    try:
        # Import the config module
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent))
        from config import agent_storage
        
        # Get local IP
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        
        # Register with multiple URLs for flexibility
        callback_url = f"http://127.0.0.1:{PORT}"
        # Register and get token
        result = agent_storage.register("local", callback_url, f"Local PC ({hostname})")
        AUTH_TOKEN = result.get("token")
        
        print(f"[Auto-registered] Agent 'local' at {callback_url}")
        print(f"[Secure Token] {AUTH_TOKEN}")
        print(f"[Config saved to] {agent_storage.agents_file}")
        
    except Exception as e:
        print(f"[Warning] Could not auto-register: {e}")
        print("[Info] Manual registration may be required")

# Windows-specific imports (only work on Windows)
try:
    import pyautogui
    import pyperclip
    from PIL import Image
    # Try to import uiautomation for advanced features
    try:
        import uiautomation as auto
        HAS_UIAUTOMATION = True
    except ImportError:
        HAS_UIAUTOMATION = False
        print("Warning: uiautomation not available. Some features will be limited.")
except ImportError as e:
    print(f"Error: Required Windows packages not installed: {e}")
    print("Run: pip install -r requirements-local.txt")
    exit(1)

# Configuration
PORT = 8006
HOST = "0.0.0.0"

# ============================================
# TOOL IMPLEMENTATIONS
# ============================================

def execute_screenshot():
    """Take a screenshot and return as base64."""
    screenshot = pyautogui.screenshot()
    buffer = BytesIO()
    screenshot.save(buffer, format="PNG")
    buffer.seek(0)
    return {"image": base64.b64encode(buffer.read()).decode()}

def execute_click(x: int, y: int, button: str = "left"):
    """Click at coordinates."""
    pyautogui.click(x, y, button=button)
    return {"status": "clicked", "x": x, "y": y, "button": button}

def execute_double_click(x: int, y: int):
    """Double-click at coordinates."""
    pyautogui.doubleClick(x, y)
    return {"status": "double_clicked", "x": x, "y": y}

def execute_right_click(x: int, y: int):
    """Right-click at coordinates."""
    pyautogui.rightClick(x, y)
    return {"status": "right_clicked", "x": x, "y": y}

def execute_type_text(text: str):
    """Type text."""
    pyautogui.typewrite(text, interval=0.02) if text.isascii() else pyautogui.write(text)
    return {"status": "typed", "text": text}

def execute_press_key(key: str):
    """Press a key."""
    pyautogui.press(key)
    return {"status": "pressed", "key": key}

def execute_hotkey(keys: str):
    """Press a hotkey combination."""
    key_list = [k.strip() for k in keys.split(",")]
    pyautogui.hotkey(*key_list)
    return {"status": "hotkey_pressed", "keys": key_list}

def execute_scroll(direction: str, amount: int = 3):
    """Scroll the screen."""
    if direction == "up":
        pyautogui.scroll(amount)
    elif direction == "down":
        pyautogui.scroll(-amount)
    elif direction == "left":
        pyautogui.hscroll(-amount)
    elif direction == "right":
        pyautogui.hscroll(amount)
    return {"status": "scrolled", "direction": direction, "amount": amount}

def execute_move_mouse(x: int, y: int):
    """Move mouse to coordinates."""
    pyautogui.moveTo(x, y)
    return {"status": "moved", "x": x, "y": y}

def execute_drag(start_x: int, start_y: int, end_x: int, end_y: int):
    """Drag from one point to another."""
    pyautogui.moveTo(start_x, start_y)
    pyautogui.drag(end_x - start_x, end_y - start_y)
    return {"status": "dragged", "from": [start_x, start_y], "to": [end_x, end_y]}

def dump_tree(control, depth=0, max_depth=4):
    """Recursively dump UI tree."""
    if depth > max_depth: return None
    
    children = []
    for child in control.GetChildren():
        # Only interesting controls
        if not child.IsOffscreen:
            node = {
                "name": child.Name,
                "type": child.ControlTypeName,
                "rect": [child.BoundingRectangle.left, child.BoundingRectangle.top, 
                        child.BoundingRectangle.right, child.BoundingRectangle.bottom] if child.BoundingRectangle else None
            }
            # Recurse
            sub = dump_tree(child, depth + 1, max_depth)
            if sub: node["children"] = sub
            children.append(node)
    
    return children if children else None

def execute_get_desktop_state():
    """Get desktop state including active window UI tree."""
    state = {
        "screen_size": pyautogui.size(),
        "mouse_position": pyautogui.position()
    }
    
    if HAS_UIAUTOMATION:
        # Get active window details (Semantic Vision)
        try:
            active = auto.GetFocusedControl().GetTopLevelControl()
            state["active_window"] = {
                "name": active.Name,
                "rect": [active.BoundingRectangle.left, active.BoundingRectangle.top, 
                        active.BoundingRectangle.right, active.BoundingRectangle.bottom],
                # Dump the tree for the active window
                "ui_tree": dump_tree(active, max_depth=3)
            }
        except Exception as e:
            state["active_window_error"] = str(e)
            
        # List all top-level windows (Basic)
        windows = []
        for win in auto.GetRootControl().GetChildren():
            try:
                if win.ClassName and win.Name:
                    rect = win.BoundingRectangle
                    windows.append({
                        "name": win.Name,
                        "class": win.ClassName,
                        "rect": [rect.left, rect.top, rect.right, rect.bottom] if rect else None
                    })
            except:
                pass
        state["windows"] = windows[:20]
    
    return state

def execute_get_screen_size():
    """Get screen dimensions."""
    size = pyautogui.size()
    return {"width": size.width, "height": size.height}

def execute_get_mouse_position():
    """Get mouse position."""
    pos = pyautogui.position()
    return {"x": pos.x, "y": pos.y}

def execute_app_launch(name: str):
    """Launch an application."""
    import os
    os.startfile(name)
    return {"status": "launched", "app": name}

def execute_app_switch(name: str):
    """Switch to an application."""
    if HAS_UIAUTOMATION:
        for win in auto.GetRootControl().GetChildren():
            try:
                if name.lower() in win.Name.lower():
                    win.SetFocus()
                    return {"status": "switched", "app": win.Name}
            except:
                pass
    return {"status": "not_found", "app": name}

def execute_app_close(name: str):
    """Close an application."""
    if HAS_UIAUTOMATION:
        for win in auto.GetRootControl().GetChildren():
            try:
                if name.lower() in win.Name.lower():
                    win.Close()
                    return {"status": "closed", "app": win.Name}
            except:
                pass
    return {"status": "not_found", "app": name}

def execute_app_list():
    """List open applications."""
    apps = []
    if HAS_UIAUTOMATION:
        for win in auto.GetRootControl().GetChildren():
            try:
                if win.Name:
                    apps.append({"name": win.Name, "class": win.ClassName})
            except:
                pass
    return {"apps": apps[:30]}

def execute_run_powershell(command: str):
    """Run PowerShell command."""
    result = subprocess.run(
        ["powershell", "-Command", command],
        capture_output=True, text=True, timeout=30
    )
    return {
        "stdout": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode
    }

def execute_run_cmd(command: str):
    """Run CMD command."""
    result = subprocess.run(
        ["cmd", "/c", command],
        capture_output=True, text=True, timeout=30
    )
    return {
        "stdout": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode
    }

def execute_file_read(path: str):
    """Read file contents."""
    with open(path, "r", encoding="utf-8") as f:
        return {"content": f.read()}

def execute_file_write(path: str, content: str):
    """Write to file."""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return {"status": "written", "path": path}

def execute_file_list(directory: str):
    """List files in directory."""
    import os
    files = os.listdir(directory)
    return {"files": files}

def execute_clipboard_copy(text: str):
    """Copy to clipboard."""
    pyperclip.copy(text)
    return {"status": "copied"}

def execute_clipboard_paste():
    """Get clipboard content."""
    return {"content": pyperclip.paste()}

def execute_chrome_open(url: str = None):
    """Open Chrome."""
    import webbrowser
    if url:
        webbrowser.open(url)
    else:
        webbrowser.open("https://google.com")
    return {"status": "opened", "url": url}

def execute_chrome_navigate(url: str):
    """Navigate to URL."""
    import webbrowser
    webbrowser.open(url)
    return {"status": "navigated", "url": url}

# Playwright Tools
try:
    from local_agent_tools.playwright_browser import browser_manager
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False
    print("Warning: Playwright not found or error importing.")

async def execute_browser_navigate(url: str):
    if not HAS_PLAYWRIGHT: return {"error": "Playwright not installed"}
    msg = await browser_manager.navigate(url)
    return {"status": "navigated", "message": msg}

async def execute_browser_click(selector: str):
    if not HAS_PLAYWRIGHT: return {"error": "Playwright not installed"}
    msg = await browser_manager.click(selector)
    return {"status": "clicked", "message": msg}

async def execute_browser_type(selector: str, text: str):
    if not HAS_PLAYWRIGHT: return {"error": "Playwright not installed"}
    msg = await browser_manager.type(selector, text)
    return {"status": "typed", "message": msg}

async def execute_browser_press(key: str):
    if not HAS_PLAYWRIGHT: return {"error": "Playwright not installed"}
    msg = await browser_manager.press(key)
    return {"status": "pressed", "message": msg}

async def execute_browser_screenshot():
    if not HAS_PLAYWRIGHT: return {"error": "Playwright not installed"}
    img = await browser_manager.screenshot()
    return {"image": img}

async def execute_browser_content():
    if not HAS_PLAYWRIGHT: return {"error": "Playwright not installed"}
    text = await browser_manager.get_content()
    return {"content": text}

def execute_wait(seconds: float):
    """Wait for seconds."""
    import time
    time.sleep(seconds)
    return {"status": "waited", "seconds": seconds}

# Command dispatcher
COMMANDS = {
    "screenshot": lambda p: execute_screenshot(),
    "click": lambda p: execute_click(p["x"], p["y"], p.get("button", "left")),
    "double_click": lambda p: execute_double_click(p["x"], p["y"]),
    "right_click": lambda p: execute_right_click(p["x"], p["y"]),
    "type_text": lambda p: execute_type_text(p["text"]),
    "press_key": lambda p: execute_press_key(p["key"]),
    "hotkey": lambda p: execute_hotkey(p["keys"]),
    "scroll": lambda p: execute_scroll(p["direction"], p.get("amount", 3)),
    "move_mouse": lambda p: execute_move_mouse(p["x"], p["y"]),
    "drag": lambda p: execute_drag(p["start_x"], p["start_y"], p["end_x"], p["end_y"]),
    "get_desktop_state": lambda p: execute_get_desktop_state(),
    "get_screen_size": lambda p: execute_get_screen_size(),
    "get_mouse_position": lambda p: execute_get_mouse_position(),
    "app_launch": lambda p: execute_app_launch(p["name"]),
    "app_switch": lambda p: execute_app_switch(p["name"]),
    "app_close": lambda p: execute_app_close(p["name"]),
    "app_list": lambda p: execute_app_list(),
    "run_powershell": lambda p: execute_run_powershell(p["command"]),
    "run_cmd": lambda p: execute_run_cmd(p["command"]),
    "file_read": lambda p: execute_file_read(p["path"]),
    "file_write": lambda p: execute_file_write(p["path"], p["content"]),
    "file_list": lambda p: execute_file_list(p["directory"]),
    "clipboard_copy": lambda p: execute_clipboard_copy(p["text"]),
    "clipboard_paste": lambda p: execute_clipboard_paste(),
    "chrome_open": lambda p: execute_chrome_open(p.get("url")),
    "chrome_navigate": lambda p: execute_chrome_navigate(p["url"]),
    "wait": lambda p: execute_wait(p["seconds"]),
    
    # Browser Tools (Playwright)
    "browser_navigate": lambda p: execute_browser_navigate(p["url"]),
    "browser_click": lambda p: execute_browser_click(p["selector"]),
    "browser_type": lambda p: execute_browser_type(p["selector"], p["text"]),
    "browser_press": lambda p: execute_browser_press(p["key"]),
    "browser_screenshot": lambda p: execute_browser_screenshot(),
    "browser_content": lambda p: execute_browser_content(),
}

# ============================================
# TERMINATOR VISION (Live Stream)
# ============================================

def get_overlay_frame():
    """Capture screen and draw semantic overlay."""
    try:
        # 1. Capture Screen
        img = pyautogui.screenshot()
        
        # 2. Draw Semantic Overlay (if uiautomation available)
        if HAS_UIAUTOMATION:
            from PIL import ImageDraw
            draw = ImageDraw.Draw(img)
            try:
                # Get active window controls (simplify for speed)
                active = auto.GetFocusedControl()
                if active:
                    # Draw active window
                    r = active.BoundingRectangle
                    draw.rectangle([r.left, r.top, r.right, r.bottom], outline="green", width=3)
                    draw.text((r.left, r.top - 15), f"ACTIVE: {active.Name}", fill="green")
                    
                    # Draw children (simple depth 1)
                    for child in active.GetChildren():
                        if not child.IsOffscreen:
                            r = child.BoundingRectangle
                            if r.width > 0 and r.height > 0:
                                draw.rectangle([r.left, r.top, r.right, r.bottom], outline="lawngreen", width=1)
            except:
                pass
        
        # 3. Convert to JPEG
        buffer = BytesIO()
        img.save(buffer, format="JPEG", quality=50) # Low quality for speed
        return buffer.getvalue()
        
    except Exception as e:
        print(f"Stream error: {e}")
        return None

async def handle_stream(request):
    """MJPEG Streaming Endpoint."""
    response = web.StreamResponse()
    response.content_type = 'multipart/x-mixed-replace; boundary=frame'
    await response.prepare(request)

    try:
        while True:
            frame = await asyncio.to_thread(get_overlay_frame)
            if frame:
                await response.write(b'--frame\r\n')
                await response.write(b'Content-Type: image/jpeg\r\n\r\n')
                await response.write(frame)
                await response.write(b'\r\n')
            await asyncio.sleep(0.2) # Limit to ~5 FPS for performance
    except:
        pass
    return response

# ============================================
# HTTP SERVER & LOGGING
# ============================================

import time
from collections import deque

# Store last 50 logs
command_logs = deque(maxlen=50)

def log_command(command: str, result: dict = None, error: str = None):
    """Log a command for the dashboard."""
    entry = {
        "timestamp": time.time(),
        "command": command,
        "status": "error" if error else "success"
    }
    if result: entry["result"] = result
    if error: entry["error"] = error
    command_logs.append(entry)

# AI Overlay
try:
    from ai_overlay import start_overlay, show_action, is_stopped, reset_stop
    HAS_OVERLAY = True
except ImportError:
    HAS_OVERLAY = False
    print("Warning: ai_overlay.py not found. Overlay disabled.")

# ============================================
# SAFETY SENTINEL
# ============================================

class CommandGuard:
    def __init__(self):
        self.safe_mode = True
        self.pending_requests = {}
        self.dangerous_commands = {
            "run_powershell", "run_cmd", "file_write", "file_delete"
        }
    
    def is_dangerous(self, command: str) -> bool:
        return command in self.dangerous_commands
    
    async def request_approval(self, command: str, params: dict) -> bool:
        """Block until approved or denied."""
        import uuid
        request_id = str(uuid.uuid4())
        event = asyncio.Event()
        
        self.pending_requests[request_id] = {
            "id": request_id,
            "command": command,
            "params": params,
            "event": event,
            "status": "pending",
            "timestamp": time.time()
        }
        
        print(f"[Safety] Blocking command '{command}' - Waiting for approval ({request_id})")
        
        # Wait for approval
        await event.wait()
        
        status = self.pending_requests[request_id]["status"]
        del self.pending_requests[request_id]
        
        return status == "approved"

    def approve(self, request_id: str):
        if request_id in self.pending_requests:
            self.pending_requests[request_id]["status"] = "approved"
            self.pending_requests[request_id]["event"].set()
            return True
        return False
        
    def deny(self, request_id: str):
        if request_id in self.pending_requests:
            self.pending_requests[request_id]["status"] = "denied"
            self.pending_requests[request_id]["event"].set()
            return True
        return False

    def set_mode(self, enabled: bool):
        self.safe_mode = enabled

guard = CommandGuard()

async def handle_safety_approve(request):
    data = await request.json()
    req_id = data.get("id")
    if guard.approve(req_id):
        return web.json_response({"status": "approved"})
    return web.json_response({"error": "Request not found"}, status=404)

async def handle_safety_deny(request):
    data = await request.json()
    req_id = data.get("id")
    if guard.deny(req_id):
        return web.json_response({"status": "denied"})
    return web.json_response({"error": "Request not found"}, status=404)

async def handle_safety_mode(request):
    data = await request.json()
    enabled = data.get("enabled", True)
    guard.set_mode(enabled)
    return web.json_response({"status": "updated", "safe_mode": guard.safe_mode})

async def handle_safety_pending(request):
    """List pending requests (exclude event objects)."""
    pending = []
    for rid, info in guard.pending_requests.items():
        pending.append({
            "id": info["id"],
            "command": info["command"],
            "params": info["params"],
            "timestamp": info["timestamp"]
        })
    return web.json_response({
        "pending": pending,
        "safe_mode": guard.safe_mode
    })

async def handle_execute(request):
    """Handle command execution requests."""
    try:
        # Auth Check
        if AUTH_TOKEN:
            auth_header = request.headers.get("Authorization")
            if not auth_header or auth_header != f"Bearer {AUTH_TOKEN}":
                log_command("unauthorized_access", error="Invalid token")
                return web.json_response({"error": "Unauthorized: Invalid or missing token"}, status=401)

        data = await request.json()
        command = data.get("command")
        params = data.get("params", {})
        
        # Safety Check
        if guard.safe_mode and guard.is_dangerous(command):
            log_command(command, error="Blocked by Safety Sentinel - Waiting for approval")
            approved = await guard.request_approval(command, params)
            if not approved:
                log_command(command, error="Denied by User")
                return web.json_response({"error": "Command denied by user security policy"}, status=403)
            log_command(command, result="Approved by User - Executing...")

        # Check if user requested stop
        if HAS_OVERLAY and is_stopped():
            reset_stop()
            error_msg = "Stopped by user via Overlay"
            log_command("stop_request", error=error_msg)
            return web.json_response({
                "error": error_msg,
                "message": "User clicked STOP button"
            }, status=400)

        if command not in COMMANDS:
            error_msg = f"Unknown command: {command}"
            log_command(command, error=error_msg)
            return web.json_response({"error": error_msg}, status=400)
        
        # Show action in overlay
        if HAS_OVERLAY:
            action_text = f"{command}"
            if params:
                param_str = ", ".join(f"{k}={v}" for k, v in list(params.items())[:2])
                action_text = f"{command}({param_str})"
            show_action(action_text)

        # Execute
        result = COMMANDS[command](params)
        if asyncio.iscoroutine(result):
            result = await result
            
        log_command(command, result=str(result)[:200] + "..." if len(str(result)) > 200 else result)
        return web.json_response(result)
    
    except Exception as e:
        log_command(command if 'command' in locals() else "unknown", error=str(e))
        return web.json_response({"error": str(e)}, status=500)
    
    except Exception as e:
        log_command(command if 'command' in locals() else "unknown", error=str(e))
        return web.json_response({"error": str(e)}, status=500)

async def handle_health(request):
    """Health check endpoint."""
    return web.json_response({"status": "healthy", "agent": "Bridge MCP Local Agent"})

async def handle_logs(request):
    """Return recent logs for dashboard."""
    return web.json_response(list(command_logs))

async def handle_index(request):
    """Serve the dashboard."""
    return web.FileResponse('./static/index.html')

def get_local_ip():
    """Get the local IP address."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

async def main():
    """Run the local agent server."""
    # Try to auto-register on startup
    await auto_register_with_bridge()

    app = web.Application()
    
    # API Routes
    app.router.add_post("/execute", handle_execute)
    app.router.add_get("/health", handle_health)
    app.router.add_get("/logs", handle_logs)
    
    # Safety Routes
    app.router.add_get("/safety/pending", handle_safety_pending)
    app.router.add_post("/safety/approve", handle_safety_approve)
    app.router.add_post("/safety/deny", handle_safety_deny)
    app.router.add_post("/safety/mode", handle_safety_mode)
    
    # Stream Route
    app.router.add_get("/stream", handle_stream)
    
    # Dashboard Routes
    app.router.add_get("/", handle_index)
    app.router.add_static("/static", "./static")
    
    # Start Overlay
    if HAS_OVERLAY:
        start_overlay()
        print("  ✅ AI Overlay started")
    
    local_ip = get_local_ip()
    
    print("=" * 60)
    print("  Bridge MCP - Local Agent")
    print("=" * 60)
    print(f"\n  Dashboard:    http://127.0.0.1:{PORT}")
    print(f"  Callback URL: http://{local_ip}:{PORT}")
    print("\n  For remote access, use ngrok:")
    print(f"    ngrok http {PORT}")
    print("=" * 60)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, HOST, PORT)
    await site.start()
    
    print(f"\n  [OK] Agent running on port {PORT}")
    print("  Press Ctrl+C to stop\n")
    
    # Keep running
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n  Agent stopped.")
