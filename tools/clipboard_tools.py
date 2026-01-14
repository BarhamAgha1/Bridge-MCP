import pyperclip

def clipboard_copy(text: str) -> str:
    """Copy text to clipboard"""
    try:
        pyperclip.copy(text)
        return "Text copied to clipboard"
    except Exception as e:
        return f"Error copying: {str(e)}"

def clipboard_paste() -> str:
    """Get current clipboard content"""
    try:
        return pyperclip.paste()
    except Exception as e:
        return f"Error pasting: {str(e)}"

def clipboard_clear() -> str:
    """Clear the clipboard"""
    try:
        pyperclip.copy("")
        return "Clipboard cleared"
    except Exception as e:
        return f"Error clearing: {str(e)}"
