"""
Bridge MCP - Cloud Relay
========================
This runs on FastMCP Cloud (Linux) and relays commands to local agents.

For FastMCP Cloud deployment:
- Entrypoint: bridge_mcp.py
- No Windows dependencies
"""

from fastmcp import FastMCP
import asyncio
import json
import os
from typing import Optional, Dict, Any
import httpx

mcp = FastMCP(
    "Bridge MCP"
)

# Store for connected local agents
# In production, this would use a proper database or Redis
connected_agents: Dict[str, Dict[str, Any]] = {}

# ============================================
# AGENT REGISTRATION
# ============================================

@mcp.tool
def register_agent(agent_id: str, callback_url: str, agent_name: str = "My PC") -> dict:
    """
    Register a local agent that will execute commands.
    
    Args:
        agent_id: Unique identifier for the agent
        callback_url: URL where the local agent is listening (e.g., http://your-ip:8006)
        agent_name: Friendly name for the agent
    
    Returns:
        Registration confirmation
    """
    connected_agents[agent_id] = {
        "callback_url": callback_url,
        "name": agent_name,
        "status": "connected"
    }
    return {
        "status": "registered",
        "agent_id": agent_id,
        "message": f"Agent '{agent_name}' registered successfully"
    }

@mcp.tool
def list_agents() -> list:
    """
    List all registered local agents.
    
    Returns:
        List of connected agents
    """
    return [
        {"id": aid, **info} 
        for aid, info in connected_agents.items()
    ]

@mcp.tool
def get_agent_status(agent_id: str = None) -> dict:
    """
    Get status of a specific agent or all agents.
    
    Args:
        agent_id: Optional agent ID. If not provided, returns all agents.
    
    Returns:
        Agent status information
    """
    if agent_id:
        if agent_id in connected_agents:
            return connected_agents[agent_id]
        return {"error": f"Agent {agent_id} not found"}
    return connected_agents

# ============================================
# COMMAND RELAY FUNCTIONS
# ============================================

async def relay_command(agent_id: str, command: str, params: dict) -> dict:
    """
    Relay a command to a local agent.
    """
    if agent_id not in connected_agents:
        # If no agent specified, try to use first available
        if connected_agents:
            agent_id = list(connected_agents.keys())[0]
        else:
            return {
                "error": "No agents connected",
                "hint": "Run local_agent.py on your Windows PC and register it first"
            }
    
    agent = connected_agents[agent_id]
    callback_url = agent["callback_url"]
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{callback_url}/execute",
                json={"command": command, "params": params}
            )
            return response.json()
    except httpx.ConnectError:
        connected_agents[agent_id]["status"] = "disconnected"
        return {"error": f"Cannot connect to agent at {callback_url}"}
    except Exception as e:
        return {"error": str(e)}

# ============================================
# PC CONTROL TOOLS (Relay to Local Agent)
# ============================================

@mcp.tool
async def screenshot(agent_id: str = None) -> dict:
    """
    Take a screenshot of the PC desktop.
    
    Args:
        agent_id: Optional. Which agent to use (uses first available if not specified)
    
    Returns:
        Base64 encoded screenshot image
    """
    return await relay_command(agent_id, "screenshot", {})

@mcp.tool
async def click(x: int, y: int, button: str = "left", agent_id: str = None) -> dict:
    """
    Click at screen coordinates.
    
    Args:
        x: X coordinate
        y: Y coordinate
        button: Mouse button ('left', 'right', 'middle')
        agent_id: Optional. Which agent to use
    
    Returns:
        Click result
    """
    return await relay_command(agent_id, "click", {"x": x, "y": y, "button": button})

@mcp.tool
async def double_click(x: int, y: int, agent_id: str = None) -> dict:
    """
    Double-click at screen coordinates.
    
    Args:
        x: X coordinate
        y: Y coordinate
        agent_id: Optional. Which agent to use
    
    Returns:
        Click result
    """
    return await relay_command(agent_id, "double_click", {"x": x, "y": y})

@mcp.tool
async def right_click(x: int, y: int, agent_id: str = None) -> dict:
    """
    Right-click at screen coordinates.
    
    Args:
        x: X coordinate
        y: Y coordinate
        agent_id: Optional. Which agent to use
    
    Returns:
        Click result
    """
    return await relay_command(agent_id, "right_click", {"x": x, "y": y})

@mcp.tool
async def type_text(text: str, agent_id: str = None) -> dict:
    """
    Type text using keyboard.
    
    Args:
        text: Text to type
        agent_id: Optional. Which agent to use
    
    Returns:
        Typing result
    """
    return await relay_command(agent_id, "type_text", {"text": text})

@mcp.tool
async def press_key(key: str, agent_id: str = None) -> dict:
    """
    Press a keyboard key.
    
    Args:
        key: Key to press (e.g., 'enter', 'tab', 'escape', 'f1')
        agent_id: Optional. Which agent to use
    
    Returns:
        Key press result
    """
    return await relay_command(agent_id, "press_key", {"key": key})

@mcp.tool
async def hotkey(keys: str, agent_id: str = None) -> dict:
    """
    Press a keyboard shortcut.
    
    Args:
        keys: Keys to press, comma-separated (e.g., 'ctrl,c' for copy)
        agent_id: Optional. Which agent to use
    
    Returns:
        Hotkey result
    """
    return await relay_command(agent_id, "hotkey", {"keys": keys})

@mcp.tool
async def scroll(direction: str, amount: int = 3, agent_id: str = None) -> dict:
    """
    Scroll the screen.
    
    Args:
        direction: Scroll direction ('up', 'down', 'left', 'right')
        amount: Scroll amount (default 3)
        agent_id: Optional. Which agent to use
    
    Returns:
        Scroll result
    """
    return await relay_command(agent_id, "scroll", {"direction": direction, "amount": amount})

@mcp.tool
async def move_mouse(x: int, y: int, agent_id: str = None) -> dict:
    """
    Move mouse to coordinates without clicking.
    
    Args:
        x: X coordinate
        y: Y coordinate
        agent_id: Optional. Which agent to use
    
    Returns:
        Move result
    """
    return await relay_command(agent_id, "move_mouse", {"x": x, "y": y})

@mcp.tool
async def drag(start_x: int, start_y: int, end_x: int, end_y: int, agent_id: str = None) -> dict:
    """
    Drag from one point to another.
    
    Args:
        start_x: Starting X coordinate
        start_y: Starting Y coordinate
        end_x: Ending X coordinate
        end_y: Ending Y coordinate
        agent_id: Optional. Which agent to use
    
    Returns:
        Drag result
    """
    return await relay_command(agent_id, "drag", {
        "start_x": start_x, "start_y": start_y,
        "end_x": end_x, "end_y": end_y
    })

@mcp.tool
async def get_desktop_state(agent_id: str = None) -> dict:
    """
    Get the current desktop state including open windows and UI elements.
    
    Args:
        agent_id: Optional. Which agent to use
    
    Returns:
        Desktop state information
    """
    return await relay_command(agent_id, "get_desktop_state", {})

@mcp.tool
async def get_screen_size(agent_id: str = None) -> dict:
    """
    Get screen dimensions.
    
    Args:
        agent_id: Optional. Which agent to use
    
    Returns:
        Screen width and height
    """
    return await relay_command(agent_id, "get_screen_size", {})

@mcp.tool
async def get_mouse_position(agent_id: str = None) -> dict:
    """
    Get current mouse cursor position.
    
    Args:
        agent_id: Optional. Which agent to use
    
    Returns:
        Mouse X and Y coordinates
    """
    return await relay_command(agent_id, "get_mouse_position", {})

@mcp.tool
async def app_launch(name: str, agent_id: str = None) -> dict:
    """
    Launch an application.
    
    Args:
        name: Application name (e.g., 'notepad', 'chrome', 'code')
        agent_id: Optional. Which agent to use
    
    Returns:
        Launch result
    """
    return await relay_command(agent_id, "app_launch", {"name": name})

@mcp.tool
async def app_switch(name: str, agent_id: str = None) -> dict:
    """
    Switch to an open application.
    
    Args:
        name: Application name to switch to
        agent_id: Optional. Which agent to use
    
    Returns:
        Switch result
    """
    return await relay_command(agent_id, "app_switch", {"name": name})

@mcp.tool
async def app_close(name: str, agent_id: str = None) -> dict:
    """
    Close an application.
    
    Args:
        name: Application name to close
        agent_id: Optional. Which agent to use
    
    Returns:
        Close result
    """
    return await relay_command(agent_id, "app_close", {"name": name})

@mcp.tool
async def app_list(agent_id: str = None) -> dict:
    """
    List all open applications.
    
    Args:
        agent_id: Optional. Which agent to use
    
    Returns:
        List of open applications
    """
    return await relay_command(agent_id, "app_list", {})

@mcp.tool
async def run_powershell(command: str, agent_id: str = None) -> dict:
    """
    Execute a PowerShell command.
    
    Args:
        command: PowerShell command to execute
        agent_id: Optional. Which agent to use
    
    Returns:
        Command output
    """
    return await relay_command(agent_id, "run_powershell", {"command": command})

@mcp.tool
async def run_cmd(command: str, agent_id: str = None) -> dict:
    """
    Execute a CMD command.
    
    Args:
        command: CMD command to execute
        agent_id: Optional. Which agent to use
    
    Returns:
        Command output
    """
    return await relay_command(agent_id, "run_cmd", {"command": command})

@mcp.tool
async def file_read(path: str, agent_id: str = None) -> dict:
    """
    Read contents of a file.
    
    Args:
        path: File path to read
        agent_id: Optional. Which agent to use
    
    Returns:
        File contents
    """
    return await relay_command(agent_id, "file_read", {"path": path})

@mcp.tool
async def file_write(path: str, content: str, agent_id: str = None) -> dict:
    """
    Write content to a file.
    
    Args:
        path: File path to write
        content: Content to write
        agent_id: Optional. Which agent to use
    
    Returns:
        Write result
    """
    return await relay_command(agent_id, "file_write", {"path": path, "content": content})

@mcp.tool
async def file_list(directory: str, agent_id: str = None) -> dict:
    """
    List files in a directory.
    
    Args:
        directory: Directory path to list
        agent_id: Optional. Which agent to use
    
    Returns:
        List of files
    """
    return await relay_command(agent_id, "file_list", {"directory": directory})

@mcp.tool
async def clipboard_copy(text: str, agent_id: str = None) -> dict:
    """
    Copy text to clipboard.
    
    Args:
        text: Text to copy
        agent_id: Optional. Which agent to use
    
    Returns:
        Copy result
    """
    return await relay_command(agent_id, "clipboard_copy", {"text": text})

@mcp.tool
async def clipboard_paste(agent_id: str = None) -> dict:
    """
    Get clipboard contents.
    
    Args:
        agent_id: Optional. Which agent to use
    
    Returns:
        Clipboard contents
    """
    return await relay_command(agent_id, "clipboard_paste", {})

@mcp.tool
async def chrome_open(url: str = None, agent_id: str = None) -> dict:
    """
    Open Chrome browser.
    
    Args:
        url: Optional URL to navigate to
        agent_id: Optional. Which agent to use
    
    Returns:
        Open result
    """
    return await relay_command(agent_id, "chrome_open", {"url": url})

@mcp.tool
async def chrome_navigate(url: str, agent_id: str = None) -> dict:
    """
    Navigate to a URL in Chrome.
    
    Args:
        url: URL to navigate to
        agent_id: Optional. Which agent to use
    
    Returns:
        Navigation result
    """
    return await relay_command(agent_id, "chrome_navigate", {"url": url})

@mcp.tool
async def wait(seconds: float, agent_id: str = None) -> dict:
    """
    Wait for specified seconds.
    
    Args:
        seconds: Number of seconds to wait
        agent_id: Optional. Which agent to use
    
    Returns:
        Wait result
    """
    return await relay_command(agent_id, "wait", {"seconds": seconds})

# ============================================
# INFO TOOLS
# ============================================

@mcp.tool
def get_info() -> dict:
    """
    Get information about Bridge MCP.
    
    Returns:
        Bridge MCP information
    """
    return {
        "name": "Bridge MCP",
        "version": "1.0.0",
        "description": "Universal PC Control for Any AI",
        "architecture": "Cloud Relay + Local Agent",
        "connected_agents": len(connected_agents),
        "github": "https://github.com/BarhamAgha1/Bridge-MCP",
        "setup_instructions": """
        To use Bridge MCP:
        1. Run local_agent.py on your Windows PC
        2. Register your agent using register_agent()
        3. Use any tool to control your PC remotely!
        """
    }

@mcp.tool
def get_setup_instructions() -> str:
    """
    Get setup instructions for Bridge MCP.
    
    Returns:
        Setup instructions
    """
    return """
    Bridge MCP Setup Instructions
    =============================
    
    Step 1: Clone the repository on your Windows PC
    ------------------------------------------------
    git clone https://github.com/BarhamAgha1/Bridge-MCP.git
    cd Bridge-MCP
    
    Step 2: Install local agent dependencies
    ----------------------------------------
    pip install -r requirements-local.txt
    
    Step 3: Run the local agent
    ---------------------------
    python local_agent.py
    
    The agent will:
    - Start a local HTTP server (default port 8006)
    - Display your callback URL
    - Wait for commands from the cloud relay
    
    Step 4: Register your agent (in your AI conversation)
    -----------------------------------------------------
    Use the register_agent tool:
    - agent_id: "my-pc" (or any unique ID)
    - callback_url: "http://your-ip:8006" (from step 3)
    - agent_name: "My Windows PC" (optional)
    
    Step 5: Start controlling your PC!
    -----------------------------------
    Use any tool like screenshot(), click(), type_text(), etc.
    
    Note: For remote access, you may need to:
    - Use ngrok: ngrok http 8006
    - Or configure port forwarding on your router
    """

# ============================================
# PROMPTS
# ============================================

@mcp.prompt
def automate_task(task_description: str) -> str:
    """
    Generate a prompt for automating a PC task.
    
    Args:
        task_description: What the user wants to accomplish
    """
    return f"""You are controlling a Windows PC using Bridge MCP tools.

Task: {task_description}

Available tools:
- screenshot() - See the current screen
- click(x, y) - Click at coordinates
- type_text(text) - Type text
- press_key(key) - Press a key
- hotkey(keys) - Press keyboard shortcut
- app_launch(name) - Launch an application
- app_switch(name) - Switch to an application
- get_desktop_state() - Get information about open windows

Strategy:
1. First, use screenshot() or get_desktop_state() to see the current screen
2. Identify the target elements and their coordinates
3. Execute actions step by step
4. Verify each action with screenshot() before proceeding

Execute this task step by step."""
