"""
Bridge MCP - Universal PC Control for Any AI
Deploy to FastMCP Cloud for worldwide access.

GitHub: https://github.com/BarhamAgha1/Bridge-MCP
"""

from fastmcp import FastMCP, Context
import base64
import subprocess
import json
from typing import Optional
from io import BytesIO

# Import tools
from tools import app_tools, input_tools, screen_tools, system_tools, browser_tools, clipboard_tools

# Initialize FastMCP server
mcp = FastMCP("Bridge MCP")



# ============================================
# APP CONTROL TOOLS
# ============================================

mcp.tool(app_tools.app_launch)
mcp.tool(app_tools.app_switch)
mcp.tool(app_tools.app_close)
mcp.tool(app_tools.app_resize)
mcp.tool(app_tools.app_move)
mcp.tool(app_tools.app_minimize)
mcp.tool(app_tools.app_maximize)
mcp.tool(app_tools.app_list)

# ============================================
# INPUT TOOLS (Mouse & Keyboard)
# ============================================

mcp.tool(input_tools.click)
mcp.tool(input_tools.double_click)
mcp.tool(input_tools.right_click)
mcp.tool(input_tools.type_text)
mcp.tool(input_tools.type_at)
mcp.tool(input_tools.press_key)
mcp.tool(input_tools.hotkey)
mcp.tool(input_tools.scroll)
mcp.tool(input_tools.drag)
mcp.tool(input_tools.move_mouse)

# ============================================
# SCREEN TOOLS
# ============================================

mcp.tool(screen_tools.screenshot)
mcp.tool(screen_tools.get_screen_size)
mcp.tool(screen_tools.get_mouse_position)
mcp.tool(screen_tools.get_desktop_state)
mcp.tool(screen_tools.find_element)
mcp.tool(screen_tools.get_pixel_color)
mcp.tool(screen_tools.wait_for_element)




# ============================================
# SYSTEM TOOLS
# ============================================

mcp.tool(system_tools.run_powershell)
mcp.tool(system_tools.run_cmd)
mcp.tool(system_tools.file_read)
mcp.tool(system_tools.file_write)
mcp.tool(system_tools.file_list)
mcp.tool(system_tools.file_exists)
mcp.tool(system_tools.get_system_info)
mcp.tool(system_tools.set_volume)
mcp.tool(system_tools.notification)

# ============================================
# BROWSER/CHROME TOOLS
# ============================================

mcp.tool(browser_tools.chrome_open)
mcp.tool(browser_tools.chrome_new_tab)
mcp.tool(browser_tools.chrome_close_tab)
mcp.tool(browser_tools.chrome_navigate)
mcp.tool(browser_tools.chrome_back)
mcp.tool(browser_tools.chrome_forward)
mcp.tool(browser_tools.chrome_refresh)
mcp.tool(browser_tools.chrome_get_url)
mcp.tool(browser_tools.chrome_get_tabs)
mcp.tool(browser_tools.chrome_switch_tab)
mcp.tool(browser_tools.chrome_search)
mcp.tool(browser_tools.chrome_scroll)
mcp.tool(browser_tools.chrome_click_element)
mcp.tool(browser_tools.chrome_fill_input)
mcp.tool(browser_tools.chrome_get_page_text)
mcp.tool(browser_tools.scrape_page)

# ============================================
# CLIPBOARD TOOLS
# ============================================

mcp.tool(clipboard_tools.clipboard_copy)
mcp.tool(clipboard_tools.clipboard_paste)
mcp.tool(clipboard_tools.clipboard_clear)




# ============================================
# UTILITY TOOLS & OTHERS
# ============================================

# NOTE: The user prompt asked for 'wait', 'alert', 'input_dialog', 'confirm_dialog', 'take_action_sequence'
# I haven't implemented these in a dedicated module, but they are simple enough to add here or in helpers.
# I will implement them inline here for simplicity as they are "new utility tools"

def wait(seconds: float) -> str:
    """Wait for specified seconds"""
    import time
    time.sleep(seconds)
    return f"Waited {seconds} seconds"

def alert(message: str) -> str:
    """Show an alert dialog box"""
    # Using pyautogui alert
    import pyautogui
    try:
        pyautogui.alert(text=message, title='Bridge MCP Alert', button='OK')
        return "Alert dismissed"
    except Exception as e:
        return f"Error showing alert: {str(e)}"

def input_dialog(prompt: str) -> str:
    """Show an input dialog and return user's response"""
    import pyautogui
    try:
        result = pyautogui.prompt(text=prompt, title='Bridge MCP Input')
        return result if result else ""
    except Exception as e:
        return f"Error showing input dialog: {str(e)}"

def confirm_dialog(message: str) -> bool:
    """Show a yes/no confirmation dialog"""
    import pyautogui
    try:
        result = pyautogui.confirm(text=message, title='Bridge MCP Confirm', buttons=['Yes', 'No'])
        return result == 'Yes'
    except Exception as e:
        return False

def take_action_sequence(actions: list) -> list:
    """
    Execute a sequence of actions. Each action is a dict:
    {"tool": "click", "params": {"x": 100, "y": 200}}
    Returns results of each action.
    """
    results = []
    # This requires looking up the tool by name.
    tool_map = {
        "click": input_tools.click,
        "type_text": input_tools.type_text,
        "wait": wait,
        "screenshot": screen_tools.screenshot
    }
    
    for action in actions:
        tool_name = action.get("tool")
        params = action.get("params", {})
        if tool_name in tool_map:
            try:
                res = tool_map[tool_name](**params)
                results.append({"tool": tool_name, "status": "success", "result": res})
            except Exception as e:
                results.append({"tool": tool_name, "status": "error", "error": str(e)})
        else:
            results.append({"tool": tool_name, "status": "error", "error": "Tool not found or not allowed in sequence"})
            
    return results

mcp.tool(wait)
mcp.tool(alert)
mcp.tool(input_dialog)
mcp.tool(confirm_dialog)
mcp.tool(take_action_sequence)




# ============================================
# RESOURCES (Read-only data endpoints)
# ============================================

@mcp.resource("desktop://state")
def get_current_state() -> str:
    """Get current desktop state as a resource"""
    # Returns JSON string
    return json.dumps(screen_tools.get_desktop_state(include_vision=False), indent=2)

@mcp.resource("desktop://screenshot")  
def get_current_screenshot() -> str:
    """Get current screenshot as base64"""
    return screen_tools.screenshot()

@mcp.resource("system://info")
def get_sys_info() -> str:
    """Get system information"""
    return json.dumps(system_tools.get_system_info(), indent=2)

# ============================================
# PROMPTS (Reusable templates)
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

Available tool categories:
1. App Control: app_launch, app_switch, app_close, app_list, etc.
2. Mouse/Keyboard: click, type_text, hotkey, scroll, drag, etc.
3. Screen: screenshot, get_desktop_state, find_element, etc.
4. System: run_powershell, file_read, file_write, etc.
5. Browser: chrome_open, chrome_navigate, chrome_new_tab, etc.
6. Clipboard: clipboard_copy, clipboard_paste

Strategy:
1. First, use get_desktop_state() or screenshot() to see the current screen
2. Identify the target elements and their coordinates
3. Execute actions step by step
4. Verify each action with screenshot() before proceeding

Execute this task step by step, explaining what you're doing."""

@mcp.prompt
def fill_form(form_description: str) -> str:
    """Generate a prompt for filling out a form"""
    return f"""You need to fill out a form on the PC.

Form details: {form_description}

Steps:
1. Take a screenshot to see the form
2. Identify all input fields and their coordinates
3. Click each field and type the appropriate value
4. Use Tab to move between fields if needed
5. Click the submit button when done

Be careful to verify each field is filled correctly."""

# ============================================
# RUN SERVER
# ============================================

if __name__ == "__main__":
    # For local testing
    mcp.run()
