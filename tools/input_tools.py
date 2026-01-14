import pyautogui
import time

# PyAutoGUI failsafe
pyautogui.FAILSAFE = True

def click(x: int, y: int, button: str = "left", clicks: int = 1) -> str:
    """Click at screen coordinates. button: 'left', 'right', 'middle'"""
    try:
        pyautogui.click(x=x, y=y, button=button, clicks=clicks)
        return f"Clicked {button} button at {x}, {y} ({clicks} times)"
    except Exception as e:
        return f"Error clicking: {str(e)}"

def double_click(x: int, y: int) -> str:
    """Double-click at coordinates"""
    try:
        pyautogui.doubleClick(x=x, y=y)
        return f"Double-clicked at {x}, {y}"
    except Exception as e:
        return f"Error double-clicking: {str(e)}"

def right_click(x: int, y: int) -> str:
    """Right-click at coordinates"""
    try:
        pyautogui.rightClick(x=x, y=y)
        return f"Right-clicked at {x}, {y}"
    except Exception as e:
        return f"Error right-clicking: {str(e)}"

def type_text(text: str, interval: float = 0.0) -> str:
    """Type text with optional interval between keystrokes"""
    try:
        pyautogui.write(text, interval=interval)
        return f"Typed text: {text}"
    except Exception as e:
        return f"Error typing: {str(e)}"

def type_at(x: int, y: int, text: str, press_enter: bool = False) -> str:
    """Click at location and type text"""
    try:
        pyautogui.click(x=x, y=y)
        time.sleep(0.5) # Wait for focus
        pyautogui.write(text)
        if press_enter:
            pyautogui.press('enter')
        return f"Typed '{text}' at {x}, {y}"
    except Exception as e:
        return f"Error typing at coords: {str(e)}"

def press_key(key: str) -> str:
    """Press a single key (e.g., 'enter', 'tab', 'escape', 'f1')"""
    try:
        pyautogui.press(key)
        return f"Pressed key: {key}"
    except Exception as e:
        return f"Error pressing key: {str(e)}"

def hotkey(keys: str) -> str:
    """Press a keyboard shortcut (e.g., hotkey('ctrl,c') for copy)"""
    try:
        key_list = [k.strip() for k in keys.split(',')]
        pyautogui.hotkey(*key_list)
        return f"Pressed hotkey: {'+'.join(key_list)}"
    except Exception as e:
        return f"Error pressing hotkey: {str(e)}"


def scroll(direction: str, amount: int = 3, x: int = None, y: int = None) -> str:
    """Scroll up/down/left/right at current or specified position"""
    try:
        if x is not None and y is not None:
             pyautogui.moveTo(x, y)
        
        # PyAutoGUI scroll is vertical. For horizontal need hscroll (if supported)
        # amount * 100 is usually a standard "click" for scroll wheels
        clicks = amount * 100
        
        if direction.lower() == 'up':
            pyautogui.scroll(clicks)
        elif direction.lower() == 'down':
            pyautogui.scroll(-clicks)
        elif direction.lower() == 'left':
            pyautogui.hscroll(-clicks)
        elif direction.lower() == 'right':
            pyautogui.hscroll(clicks)
        else:
            return f"Unknown direction: {direction}"
            
        return f"Scrolled {direction} by {amount}"
    except Exception as e:
        return f"Error scrolling: {str(e)}"

def drag(start_x: int, start_y: int, end_x: int, end_y: int) -> str:
    """Drag from start to end coordinates"""
    try:
        pyautogui.moveTo(start_x, start_y)
        pyautogui.dragTo(end_x, end_y, duration=0.5)
        return f"Dragged from {start_x},{start_y} to {end_x},{end_y}"
    except Exception as e:
        return f"Error dragging: {str(e)}"

def move_mouse(x: int, y: int) -> str:
    """Move mouse to coordinates without clicking"""
    try:
        pyautogui.moveTo(x, y)
        return f"Moved mouse to {x}, {y}"
    except Exception as e:
        return f"Error moving mouse: {str(e)}"
