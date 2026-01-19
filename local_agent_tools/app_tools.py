from fastmcp import FastMCP, Context
import uiautomation as auto
import subprocess
import time
import psutil

# We don't initialize FastMCP here, we just define tools
# The main server will import these. 
# However, FastMCP usage usually requires the @mcp decorator on the object.
# Since we are splitting into modules, we can either pass the mcp object or usage a different pattern.
# For FastMCP, the easiest way with multiple files is often to have the mcp object imported or passed.
# BUT, the user prompt showed:
# @mcp.tool
# def app_launch...
# This implies 'mcp' is available globally or imported.
# To make this clean in a multi-file setup with FastMCP:
# We can create a "context" or shared mcp instance, OR we can define functions and register them later.
# Given the prompt structure, I will define them as standard functions and the main file will import and register them,
# OR I will use a Context-like approach if FastMCP supports blueprints/routers (which it does in newer versions, but let's stick to simple).
# The prompt showed the single file structure. For multi-file, I will assume we can import 'mcp' from a shared place OR just define functions
# and the main bridge_mcp.py will do: mcp.tool(app_launch).
#
# Actually, FastMCP 2.0+ usually supports:
# from fastmcp import FastMCP
# mcp = FastMCP(...)
# @mcp.tool
#
# To avoid circular imports, I'll define functions here and in main.py I will do:
# import tools.app_tools as app_tools
# mcp.tool(app_tools.app_launch)
# ...
# This is the cleanest way without circular dependency on the 'mcp' object.

def app_launch(name: str) -> str:
    """Launch an application by name (e.g., 'notepad', 'chrome', 'vscode')"""
    try:
        # Simple common mappings
        apps = {
            'notepad': 'notepad.exe',
            'calc': 'calc.exe',
            'chrome': 'chrome.exe',
            'edge': 'msedge.exe',
            'code': 'code',
            'vscode': 'code',
            'explorer': 'explorer.exe',
            'cmd': 'cmd.exe',
            'powershell': 'powershell.exe'
        }
        
        cmd = apps.get(name.lower(), name)
        subprocess.Popen(cmd, shell=True)
        return f"Launched {name}"
    except Exception as e:
        return f"Failed to launch {name}: {str(e)}"

def app_switch(name: str) -> str:
    """Switch to an open application window"""
    try:
        # Search for window
        window = auto.WindowControl(searchDepth=2, Name=name, SubName=name, RegexName=name)
        if not window.Exists(0, 1):
             # Try stricter search if regex/subname matched too many or none
             window = auto.WindowControl(searchDepth=2, RegexName=f".*{name}.*", CaseSensitive=False)
        
        if window.Exists(0, 1):
            window.SetFocus()
            return f"Switched to {window.Name}"
        else:
            return f"Could not find window matching '{name}'"
    except Exception as e:
        return f"Error switching to {name}: {str(e)}"

def app_close(name: str) -> str:
    """Close an application"""
    try:
        window = auto.WindowControl(searchDepth=2, RegexName=f".*{name}.*", CaseSensitive=False)
        if window.Exists(0, 1):
            window.GetWindowPattern().Close()
            return f"Closed {name}"
        else:
            return f"Could not find window '{name}' to close"
    except Exception as e:
        return f"Error closing {name}: {str(e)}"

def app_resize(name: str, width: int, height: int) -> str:
    """Resize an application window"""
    try:
        window = auto.WindowControl(searchDepth=2, RegexName=f".*{name}.*", CaseSensitive=False)
        if window.Exists(0, 1):
            window.Resize(width, height)
            return f"Resized {name} to {width}x{height}"
        return f"Window '{name}' not found"
    except Exception as e:
        return f"Error resizing {name}: {str(e)}"

def app_move(name: str, x: int, y: int) -> str:
    """Move an application window to coordinates"""
    try:
        window = auto.WindowControl(searchDepth=2, RegexName=f".*{name}.*", CaseSensitive=False)
        if window.Exists(0, 1):
            window.Move(x, y)
            return f"Moved {name} to {x},{y}"
        return f"Window '{name}' not found"
    except Exception as e:
        return f"Error moving {name}: {str(e)}"

def app_minimize(name: str) -> str:
    """Minimize an application"""
    try:
        window = auto.WindowControl(searchDepth=2, RegexName=f".*{name}.*", CaseSensitive=False)
        if window.Exists(0, 1):
            window.GetWindowPattern().SetWindowVisualState(auto.WindowVisualState.Minimized)
            return f"Minimized {name}"
        return f"Window '{name}' not found"
    except Exception as e:
        return f"Error minimizing {name}: {str(e)}"

def app_maximize(name: str) -> str:
    """Maximize an application"""
    try:
        window = auto.WindowControl(searchDepth=2, RegexName=f".*{name}.*", CaseSensitive=False)
        if window.Exists(0, 1):
            window.GetWindowPattern().SetWindowVisualState(auto.WindowVisualState.Maximized)
            return f"Maximized {name}"
        return f"Window '{name}' not found"
    except Exception as e:
        return f"Error maximizing {name}: {str(e)}"

def app_list() -> list:
    """List all open applications with their window info"""
    apps = []
    try:
        root = auto.GetRootControl()
        for window in root.GetChildren():
            if window.ControlTypeName == "WindowControl":
                # Filter out some system windows/overlays ideally, but keep it simple
                rect = window.BoundingRectangle
                apps.append({
                    "name": window.Name,
                    "handle": window.NativeWindowHandle,
                    "process_id": window.ProcessId,
                    "rect": {"left": rect.left, "top": rect.top, "width": rect.width(), "height": rect.height()}
                })
    except Exception as e:
        pass # Return what we have
    return apps
