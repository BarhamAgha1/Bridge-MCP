import pyautogui
import uiautomation as auto
import base64
import io
from PIL import Image
import time
import json

# Note: We'll assume utils.vision might be used if available, or just generic logic
try:
    from ..utils import vision
except ImportError:
    vision = None

def screenshot(region: dict = None) -> str:
    """Take a screenshot. Optional region: {x, y, width, height}. Returns base64 image."""
    try:
        if region:
            img = pyautogui.screenshot(region=(region.get('x'), region.get('y'), region.get('width'), region.get('height')))
        else:
            img = pyautogui.screenshot()
        
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return img_str
    except Exception as e:
        return f"Error taking screenshot: {str(e)}"

def get_screen_size() -> dict:
    """Get screen dimensions: {width, height}"""
    width, height = pyautogui.size()
    return {"width": width, "height": height}

def get_mouse_position() -> dict:
    """Get current mouse position: {x, y}"""
    x, y = pyautogui.position()
    return {"x": x, "y": y}

def get_desktop_state(include_vision: bool = True) -> dict:
    """
    Get comprehensive desktop state:
    - Focused app
    - All open apps with positions
    - Interactive UI elements with coordinates
    - Scrollable elements
    - Optional: screenshot for vision analysis
    """
    state = {
        "timestamp": time.time(),
        "mouse": get_mouse_position(),
        "screen": get_screen_size(),
        "focused_window": None,
        "apps": []
    }
    
    try:
        focused = auto.GetFocusedControl()
        if focused:
            rect = focused.BoundingRectangle
            state["focused_window"] = {
                "name": focused.Name,
                "type": focused.ControlTypeName,
                "rect": {"left": rect.left, "top": rect.top, "width": rect.width(), "height": rect.height()}
            }
            
        root = auto.GetRootControl()
        for window in root.GetChildren():
            if window.ControlTypeName == "WindowControl":
                rect = window.BoundingRectangle
                state["apps"].append({
                    "name": window.Name,
                    "handle": window.NativeWindowHandle, # Convert to int if needed
                    "rect": {"left": rect.left, "top": rect.top, "width": rect.width(), "height": rect.height()}
                })
                
        if include_vision:
            state["screenshot"] = screenshot() # Base64
            
    except Exception as e:
        state["error"] = str(e)
        
    return state

def find_element(text: str) -> dict:
    """Find UI element by text/label and return its coordinates"""
    try:
        # Search by Name
        control = auto.Control(searchDepth=5, Name=text, SubName=text, RegexName=text)
        if not control.Exists(0, 1):
            # Try deeper search or search by AutomationId
            control = auto.Control(searchDepth=5, AutomationId=text)
            
        if control.Exists(0, 1):
            rect = control.BoundingRectangle
            center_x = rect.left + rect.width() // 2
            center_y = rect.top + rect.height() // 2
            return {
                "found": True,
                "x": center_x,
                "y": center_y,
                "rect": {"left": rect.left, "top": rect.top, "width": rect.width(), "height": rect.height()},
                "name": control.Name
            }
        
        return {"found": False, "error": "Element not found"}
    except Exception as e:
        return {"found": False, "error": str(e)}

def get_pixel_color(x: int, y: int) -> str:
    """Get the color of a pixel at coordinates"""
    try:
        if x < 0 or y < 0: return "Invalid coordinates"
        # snapshot of 1 pixel
        img = pyautogui.screenshot(region=(x, y, 1, 1))
        color = img.getpixel((0, 0))
        return f"RGB{color}"
    except Exception as e:
        return f"Error getting pixel color: {str(e)}"

def wait_for_element(text: str, timeout: int = 10) -> dict:
    """Wait for a UI element to appear, return its coordinates"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        result = find_element(text)
        if result.get("found"):
            return result
        time.sleep(1)
    return {"found": False, "error": "Timeout waiting for element"}
