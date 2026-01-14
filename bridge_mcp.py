"""
Bridge MCP - Cloud Relay with Persistent Storage
=================================================
This MCP server maintains agent registrations across sessions.

Key Features:
- Persistent agent storage (survives restarts)
- Auto-discovery of local agent
- Works across all Claude Code/Desktop sessions
"""

from fastmcp import FastMCP
import asyncio
import json
import os
from typing import Optional, Dict, Any
import httpx

# Import our persistent storage
try:
    from config import agent_storage, config
except ImportError:
    # Fallback for when running standalone
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    from config import agent_storage, config

mcp = FastMCP("Bridge MCP")

# ============================================
# AUTO-DISCOVERY ON STARTUP
# ============================================

async def auto_discover_local_agent():
    """
    Automatically discover and register local agent if running.
    Called on server startup.
    """
    local_url = f"http://127.0.0.1:{config.get('local_agent_port', 8006)}"
    
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            response = await client.get(f"{local_url}/health")
            if response.status_code == 200:
                # Local agent is running! Auto-register if not already
                existing = agent_storage.get("local")
                if not existing or existing.get("callback_url") != local_url:
                    agent_storage.register("local", local_url, "Local PC (Auto-discovered)")
                agent_storage.update_status("local", "connected")
                return True
    except:
        pass
    return False

# Run auto-discovery on import (when MCP starts)
try:
    asyncio.get_event_loop().run_until_complete(auto_discover_local_agent())
except:
    pass  # May fail if no event loop yet, that's OK

# ============================================
# AGENT REGISTRATION (PERSISTENT)
# ============================================

@mcp.tool
def register_agent(agent_id: str, callback_url: str, agent_name: str = "My PC") -> dict:
    """
    Register a local agent that will execute commands.
    This registration is PERSISTENT and survives server restarts.
    
    Args:
        agent_id: Unique identifier for the agent (e.g., "my-pc", "work-laptop")
        callback_url: URL where the local agent is listening (e.g., http://127.0.0.1:8006)
        agent_name: Friendly name for the agent
    
    Returns:
        Registration confirmation
    """
    return agent_storage.register(agent_id, callback_url, agent_name)

@mcp.tool
def unregister_agent(agent_id: str) -> dict:
    """
    Remove a registered agent.
    
    Args:
        agent_id: ID of the agent to remove
    
    Returns:
        Removal confirmation
    """
    return agent_storage.unregister(agent_id)

@mcp.tool
def list_agents() -> dict:
    """
    List all registered agents (persistent across sessions).
    
    Returns:
        Dictionary of all registered agents with their status
    """
    agents = agent_storage.get_all()
    return {
        "agents": [{"id": aid, **info} for aid, info in agents.items()],
        "count": len(agents),
        "config_location": str(agent_storage.agents_file)
    }

@mcp.tool
async def check_agent_health(agent_id: str = None) -> dict:
    """
    Check if an agent is online and responding.
    
    Args:
        agent_id: Optional. Agent to check (checks all if not specified)
    
    Returns:
        Health status of agent(s)
    """
    results = {}
    agents = agent_storage.get_all()
    
    if agent_id:
        if agent_id not in agents:
            return {"error": f"Agent {agent_id} not registered"}
        agents = {agent_id: agents[agent_id]}
    
    for aid, info in agents.items():
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{info['callback_url']}/health")
                if response.status_code == 200:
                    agent_storage.update_status(aid, "connected")
                    results[aid] = {"status": "healthy", "url": info['callback_url']}
                else:
                    agent_storage.update_status(aid, "error")
                    results[aid] = {"status": "error", "code": response.status_code}
        except httpx.ConnectError:
            agent_storage.update_status(aid, "disconnected")
            results[aid] = {"status": "disconnected", "url": info['callback_url']}
        except Exception as e:
            results[aid] = {"status": "error", "error": str(e)}
    
    return results

@mcp.tool
def set_default_agent(agent_id: str) -> dict:
    """
    Set an agent as the default for all commands.
    
    Args:
        agent_id: Agent to set as default
    
    Returns:
        Confirmation
    """
    return agent_storage.set_default(agent_id)

# ============================================
# COMMAND RELAY (Uses Persistent Storage)
# ============================================

async def relay_command(agent_id: Optional[str], command: str, params: dict) -> dict:
    """
    Relay a command to a local agent.
    Uses persistent storage to find agents.
    """
    agents = agent_storage.get_all()
    
    # If no agent specified, try to find one
    if not agent_id:
        # First, try auto-discovery
        if config.get("auto_connect_localhost", True):
            if await auto_discover_local_agent():
                agent_id = "local"
        
        # Use first available agent
        if not agent_id and agents:
            agent_id = list(agents.keys())[0]
    
    if not agent_id or agent_id not in agents:
        return {
            "error": "No agents available",
            "hint": "Start local_agent.py on your Windows PC. It will auto-register.",
            "registered_agents": list(agents.keys()) if agents else [],
            "config_file": str(agent_storage.agents_file)
        }
    
    agent = agents[agent_id]
    callback_url = agent["callback_url"]
    token = agent.get("token")
    
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    try:
        async with httpx.AsyncClient(timeout=config.get("connection_timeout", 30)) as client:
            response = await client.post(
                f"{callback_url}/execute",
                json={"command": command, "params": params},
                headers=headers
            )
            agent_storage.update_status(agent_id, "connected")
            return response.json()
    except httpx.ConnectError:
        agent_storage.update_status(agent_id, "disconnected")
        return {
            "error": f"Cannot connect to agent '{agent_id}' at {callback_url}",
            "hint": "Make sure local_agent.py is running on your PC"
        }
    except Exception as e:
        return {"error": str(e)}

# ============================================
# PC CONTROL TOOLS (Same as before, but using persistent storage)
# ============================================

@mcp.tool
async def screenshot(agent_id: str = None) -> dict:
    """Take a screenshot of the PC desktop."""
    return await relay_command(agent_id, "screenshot", {})

@mcp.tool
async def click(x: int, y: int, button: str = "left", agent_id: str = None) -> dict:
    """Click at screen coordinates."""
    return await relay_command(agent_id, "click", {"x": x, "y": y, "button": button})

@mcp.tool
async def double_click(x: int, y: int, agent_id: str = None) -> dict:
    """Double-click at screen coordinates."""
    return await relay_command(agent_id, "double_click", {"x": x, "y": y})

@mcp.tool
async def right_click(x: int, y: int, agent_id: str = None) -> dict:
    """Right-click at screen coordinates."""
    return await relay_command(agent_id, "right_click", {"x": x, "y": y})

@mcp.tool
async def type_text(text: str, agent_id: str = None) -> dict:
    """Type text using keyboard."""
    return await relay_command(agent_id, "type_text", {"text": text})

@mcp.tool
async def press_key(key: str, agent_id: str = None) -> dict:
    """Press a keyboard key."""
    return await relay_command(agent_id, "press_key", {"key": key})

@mcp.tool
async def hotkey(keys: str, agent_id: str = None) -> dict:
    """Press a keyboard shortcut (e.g., 'ctrl,c' for copy)."""
    return await relay_command(agent_id, "hotkey", {"keys": keys})

@mcp.tool
async def scroll(direction: str, amount: int = 3, agent_id: str = None) -> dict:
    """Scroll the screen."""
    return await relay_command(agent_id, "scroll", {"direction": direction, "amount": amount})

@mcp.tool
async def move_mouse(x: int, y: int, agent_id: str = None) -> dict:
    """Move mouse to coordinates without clicking."""
    return await relay_command(agent_id, "move_mouse", {"x": x, "y": y})

@mcp.tool
async def drag(start_x: int, start_y: int, end_x: int, end_y: int, agent_id: str = None) -> dict:
    """Drag from one point to another."""
    return await relay_command(agent_id, "drag", {
        "start_x": start_x, "start_y": start_y,
        "end_x": end_x, "end_y": end_y
    })

@mcp.tool
async def get_desktop_state(agent_id: str = None) -> dict:
    """Get the current desktop state including open windows."""
    return await relay_command(agent_id, "get_desktop_state", {})

@mcp.tool
async def get_screen_size(agent_id: str = None) -> dict:
    """Get screen dimensions."""
    return await relay_command(agent_id, "get_screen_size", {})

@mcp.tool
async def get_mouse_position(agent_id: str = None) -> dict:
    """Get current mouse cursor position."""
    return await relay_command(agent_id, "get_mouse_position", {})

@mcp.tool
async def app_launch(name: str, agent_id: str = None) -> dict:
    """Launch an application."""
    return await relay_command(agent_id, "app_launch", {"name": name})

@mcp.tool
async def app_switch(name: str, agent_id: str = None) -> dict:
    """Switch to an open application."""
    return await relay_command(agent_id, "app_switch", {"name": name})

@mcp.tool
async def app_close(name: str, agent_id: str = None) -> dict:
    """Close an application."""
    return await relay_command(agent_id, "app_close", {"name": name})

@mcp.tool
async def app_list(agent_id: str = None) -> dict:
    """List all open applications."""
    return await relay_command(agent_id, "app_list", {})

@mcp.tool
async def run_powershell(command: str, agent_id: str = None) -> dict:
    """Execute a PowerShell command."""
    return await relay_command(agent_id, "run_powershell", {"command": command})

@mcp.tool
async def run_cmd(command: str, agent_id: str = None) -> dict:
    """Execute a CMD command."""
    return await relay_command(agent_id, "run_cmd", {"command": command})

@mcp.tool
async def file_read(path: str, agent_id: str = None) -> dict:
    """Read contents of a file."""
    return await relay_command(agent_id, "file_read", {"path": path})

@mcp.tool
async def file_write(path: str, content: str, agent_id: str = None) -> dict:
    """Write content to a file."""
    return await relay_command(agent_id, "file_write", {"path": path, "content": content})

@mcp.tool
async def file_list(directory: str, agent_id: str = None) -> dict:
    """List files in a directory."""
    return await relay_command(agent_id, "file_list", {"directory": directory})

@mcp.tool
async def clipboard_copy(text: str, agent_id: str = None) -> dict:
    """Copy text to clipboard."""
    return await relay_command(agent_id, "clipboard_copy", {"text": text})

@mcp.tool
async def clipboard_paste(agent_id: str = None) -> dict:
    """Get clipboard contents."""
    return await relay_command(agent_id, "clipboard_paste", {})

# ============================================
# BROWSER TOOLS (Playwright - Advanced)
# ============================================

@mcp.tool
async def browser_navigate(url: str, agent_id: str = None) -> dict:
    """Navigate to a URL using Playwright (Advanced)."""
    return await relay_command(agent_id, "browser_navigate", {"url": url})

@mcp.tool
async def browser_click(selector: str, agent_id: str = None) -> dict:
    """Click an element by CSS selector."""
    return await relay_command(agent_id, "browser_click", {"selector": selector})

@mcp.tool
async def browser_type(selector: str, text: str, agent_id: str = None) -> dict:
    """Type text into an element by CSS selector."""
    return await relay_command(agent_id, "browser_type", {"selector": selector, "text": text})

@mcp.tool
async def browser_press(key: str, agent_id: str = None) -> dict:
    """Press a key (e.g., 'Enter', 'ArrowDown')."""
    return await relay_command(agent_id, "browser_press", {"key": key})

@mcp.tool
async def browser_screenshot(agent_id: str = None) -> dict:
    """Take a screenshot of the browser page."""
    return await relay_command(agent_id, "browser_screenshot", {})

@mcp.tool
async def browser_content(agent_id: str = None) -> dict:
    """Get the text content of the browser page."""
    return await relay_command(agent_id, "browser_content", {})

@mcp.tool
async def chrome_open(url: str = None, agent_id: str = None) -> dict:
    """Open Chrome browser."""
    return await relay_command(agent_id, "chrome_open", {"url": url})

@mcp.tool
async def chrome_navigate(url: str, agent_id: str = None) -> dict:
    """Navigate to a URL in Chrome."""
    return await relay_command(agent_id, "chrome_navigate", {"url": url})

@mcp.tool
async def wait(seconds: float, agent_id: str = None) -> dict:
    """Wait for specified seconds."""
    return await relay_command(agent_id, "wait", {"seconds": seconds})

# ============================================
# INFO TOOLS
# ============================================

@mcp.tool
def get_info() -> dict:
    """Get information about Bridge MCP."""
    agents = agent_storage.get_all()
    return {
        "name": "Bridge MCP",
        "version": "2.0.0",
        "description": "Universal PC Control for Any AI - with Persistent Storage",
        "architecture": "Cloud Relay + Local Agent + Persistent Config",
        "connected_agents": len(agents),
        "agents": list(agents.keys()),
        "config_directory": str(agent_storage.agents_file.parent),
        "auto_discovery": config.get("auto_connect_localhost", True),
        "github": "https://github.com/BarhamAgha1/Bridge-MCP"
    }

@mcp.tool
def get_setup_instructions() -> str:
    """Get setup instructions for Bridge MCP."""
    return """
    Bridge MCP Setup Instructions (v2.0 - Persistent Storage)
    ==========================================================
    
    QUICK START (Recommended):
    --------------------------
    1. Run local_agent.py on your Windows PC (keep it running)
    2. That's it! Bridge MCP auto-discovers and remembers your agent.
    
    The agent registration is PERSISTENT - it survives across:
    - Claude Code sessions
    - Claude Desktop restarts
    - Computer reboots (as long as local_agent.py is running)
    
    MANUAL REGISTRATION (if needed):
    ---------------------------------
    Use register_agent("my-pc", "http://127.0.0.1:8006", "My PC")
    
    CHECK STATUS:
    -------------
    - list_agents() - See all registered agents
    - check_agent_health() - Verify agents are online
    
    CONFIG LOCATION:
    ----------------
    Windows: %APPDATA%/bridge-mcp/agents.json
    Linux/Mac: ~/.config/bridge-mcp/agents.json
    """

# ============================================
# ENTRY POINT
# ============================================

if __name__ == "__main__":
    mcp.run()
