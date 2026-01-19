import pyautogui
import time
import pyperclip
import webbrowser
import requests
from bs4 import BeautifulSoup

def chrome_open(url: str = None) -> str:
    """Open Chrome, optionally navigate to URL"""
    try:
        # If URL provided, use webbrowser which usually opens default browser
        if url:
            webbrowser.get('chrome').open(url) # explicit chrome if registered, else default
            # or just generic:
            # webbrowser.open(url)
        else:
            # Launch chrome simply
            pyautogui.press('win')
            time.sleep(0.5)
            pyautogui.write('chrome')
            pyautogui.press('enter')
        return "Opened Chrome"
    except Exception as e:
        # Fallback to generic open
        try:
            webbrowser.open(url if url else 'about:blank')
            return "Opened default browser"
        except Exception as e2:
            return f"Error opening chrome: {str(e2)}"

def chrome_new_tab(url: str = None) -> str:
    """Open a new Chrome tab, optionally navigate to URL"""
    try:
        pyautogui.hotkey('ctrl', 't')
        time.sleep(0.5)
        if url:
            pyautogui.write(url)
            pyautogui.press('enter')
        return "Opened new tab"
    except Exception as e:
        return f"Error opening tab: {str(e)}"

def chrome_close_tab() -> str:
    """Close the current Chrome tab"""
    try:
        pyautogui.hotkey('ctrl', 'w')
        return "Closed tab"
    except Exception as e:
        return f"Error closing tab: {str(e)}"

def chrome_navigate(url: str) -> str:
    """Navigate current tab to URL"""
    try:
        pyautogui.hotkey('ctrl', 'l') # Focus address bar
        time.sleep(0.2)
        pyautogui.write(url)
        pyautogui.press('enter')
        return f"Navigated to {url}"
    except Exception as e:
        return f"Error navigating: {str(e)}"

def chrome_back() -> str:
    """Go back in browser history"""
    pyautogui.hotkey('alt', 'left')
    return "Went back"

def chrome_forward() -> str:
    """Go forward in browser history"""
    pyautogui.hotkey('alt', 'right')
    return "Went forward"

def chrome_refresh() -> str:
    """Refresh the current page"""
    pyautogui.press('f5')
    return "Refreshed page"

def chrome_get_url() -> str:
    """Get the current tab's URL"""
    try:
        # Focus address bar, copy
        pyautogui.hotkey('ctrl', 'l')
        time.sleep(0.2)
        pyautogui.hotkey('ctrl', 'c')
        time.sleep(0.1)
        url = pyperclip.paste()
        # click away to unfocus? maybe press esc
        pyautogui.press('esc')
        return url
    except Exception as e:
        return f"Error getting URL: {str(e)}"

def chrome_get_tabs() -> list:
    """Get list of all open Chrome tabs"""
    # Impossible without CDP or Accessibility API deep dive.
    return ["Getting tab list requires Chrome DevTools Protocol which is not configured."]

def chrome_switch_tab(index: int) -> str:
    """Switch to a specific tab by index"""
    try:
        pyautogui.hotkey('ctrl', str(index)) # 1-8 works, 9 is last
        return f"Switched to tab {index}"
    except Exception as e:
        return f"Error switching tab: {str(e)}"

def chrome_search(query: str) -> str:
    """Search in Chrome (opens new tab with Google search)"""
    return chrome_new_tab(f"google.com/search?q={query.replace(' ', '+')}")

def chrome_scroll(direction: str, amount: int = 3) -> str:
    """Scroll the current Chrome page"""
    # Reuse generic scroll or specifically
    clicks = amount * 100
    if direction == 'down':
        pyautogui.scroll(-clicks)
    elif direction == 'up':
        pyautogui.scroll(clicks)
    return f"Scrolled {direction}"

def chrome_click_element(selector: str) -> str:
    """Click an element by CSS selector (uses Chrome DevTools Protocol if available)"""
    return "Clicking by selector requires CDP. Not implemented in this basic version."

def chrome_fill_input(selector: str, text: str) -> str:
    """Fill an input field by CSS selector"""
    return "Filling by selector requires CDP. Not implemented in this basic version."

def chrome_get_page_text() -> str:
    """Get all visible text from current page"""
    try:
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.2)
        pyautogui.hotkey('ctrl', 'c')
        time.sleep(0.2)
        text = pyperclip.paste()
        pyautogui.click(x=200, y=200) # Unselect approximately
        return text
    except Exception as e:
        return f"Error getting page text: {str(e)}"

def scrape_page(url: str = None) -> dict:
    """Scrape current page or specified URL, return structured data"""
    # If URL is provided, we can use requests + bs4 (lightweight)
    if url:
        try:
            resp = requests.get(url)
            soup = BeautifulSoup(resp.text, 'html.parser')
            return {
                "title": soup.title.string if soup.title else "",
                "text": soup.get_text()[:5000] # Cap text
            }
        except Exception as e:
            return {"error": str(e)}
    else:
        # Scrape current active tab?
        return {"error": "Scraping current tab requires CDP. Provide a URL argument."}
