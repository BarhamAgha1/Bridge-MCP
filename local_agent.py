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

def execute_get_desktop_state():
    """Get desktop state."""
    state = {
        "screen_size": pyautogui.size(),
        "mouse_position": pyautogui.position()
    }
    
    if HAS_UIAUTOMATION:
        # Get open windows
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
        state["windows"] = windows[:20]  # Limit to 20 windows
    
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
}

# ============================================
# HTTP SERVER
# ============================================

async def handle_execute(request):
    """Handle command execution requests."""
    try:
        data = await request.json()
        command = data.get("command")
        params = data.get("params", {})
        
        if command not in COMMANDS:
            return web.json_response({"error": f"Unknown command: {command}"}, status=400)
        
        result = COMMANDS[command](params)
        return web.json_response(result)
    
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)

async def handle_health(request):
    """Health check endpoint."""
    return web.json_response({"status": "healthy", "agent": "Bridge MCP Local Agent"})

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
    app = web.Application()
    app.router.add_post("/execute", handle_execute)
    app.router.add_get("/health", handle_health)
    
    local_ip = get_local_ip()
    
    print("=" * 60)
    print("  Bridge MCP - Local Agent")
    print("=" * 60)
    print(f"\n  Local URL:    http://127.0.0.1:{PORT}")
    print(f"  Network URL:  http://{local_ip}:{PORT}")
    print(f"\n  Register this agent using:")
    print(f"    callback_url: http://{local_ip}:{PORT}")
    print("\n  For remote access, use ngrok:")
    print(f"    ngrok http {PORT}")
    print("=" * 60)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, HOST, PORT)
    await site.start()
    
    print(f"\n  ✅ Agent running on port {PORT}")
    print("  Press Ctrl+C to stop\n")
    
    # Keep running
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n  Agent stopped.")
