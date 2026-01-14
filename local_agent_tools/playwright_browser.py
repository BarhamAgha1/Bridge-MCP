"""
Bridge MCP - Playwright Browser Automation
==========================================
Advanced browser control using Playwright.
Allows clicking, typing, extracting text, and full automation.
"""

from playwright.async_api import async_playwright, Browser, BrowserContext, Page
import asyncio
import base64
from typing import Optional, Dict, Any

class BrowserManager:
    def __init__(self):
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.started = False

    async def start(self):
        """Start the browser."""
        if self.started:
            return
        
        try:
            self.playwright = await async_playwright().start()
            # Launch headless=False so user can see it
            self.browser = await self.playwright.chromium.launch(headless=False)
            self.context = await self.browser.new_context(
                viewport={"width": 1280, "height": 720}
            )
            self.page = await self.context.new_page()
            self.started = True
            print("[Browser] Started Playwright session")
        except Exception as e:
            print(f"[Browser] Error starting: {e}")
            raise

    async def ensure_page(self):
        """Ensure we have a valid page."""
        if not self.started:
            await self.start()
        if not self.page or self.page.is_closed():
            self.page = await self.context.new_page()

    async def navigate(self, url: str):
        """Navigate to a URL."""
        await self.ensure_page()
        try:
            if not url.startswith("http"):
                url = "https://" + url
            await self.page.goto(url)
            return f"Navigated to {url}"
        except Exception as e:
            return f"Error navigating: {e}"

    async def click(self, selector: str):
        """Click an element."""
        await self.ensure_page()
        try:
            await self.page.click(selector, timeout=5000)
            return f"Clicked '{selector}'"
        except Exception as e:
            return f"Error clicking '{selector}': {e}"

    async def type(self, selector: str, text: str):
        """Type into an element."""
        await self.ensure_page()
        try:
            await self.page.fill(selector, text, timeout=5000)
            return f"Typed into '{selector}'"
        except Exception as e:
            return f"Error typing into '{selector}': {e}"

    async def press(self, key: str):
        """Press a key."""
        await self.ensure_page()
        try:
            await self.page.keyboard.press(key)
            return f"Pressed '{key}'"
        except Exception as e:
            return f"Error pressing '{key}': {e}"

    async def screenshot(self):
        """Take a screenshot of the browser page."""
        await self.ensure_page()
        try:
            bytes_img = await self.page.screenshot()
            return base64.b64encode(bytes_img).decode()
        except Exception as e:
            raise e

    async def get_content(self):
        """Get page text content."""
        await self.ensure_page()
        try:
            # Get readable text, maybe use simple innerText of body
            text = await self.page.evaluate("document.body.innerText")
            return text[:10000] # Limit
        except Exception as e:
            return f"Error getting content: {e}"

    async def close(self):
        """Close the browser."""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        self.started = False

# Global instance
browser_manager = BrowserManager()
