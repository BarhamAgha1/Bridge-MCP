import pystray
from PIL import Image, ImageDraw
import threading
import asyncio
import webbrowser
import os
import sys

# Import local agent
import local_agent

# Global state
agent_thread = None
loop = None
stop_event = threading.Event()

def create_icon_image():
    """Create a simple icon for the tray."""
    width = 64
    height = 64
    image = Image.new('RGB', (width, height), (30, 30, 30))
    dc = ImageDraw.Draw(image)
    
    # Draw a blue circle (Bridge)
    dc.ellipse((8, 8, 56, 56), fill=(65, 105, 225))
    dc.text((20, 20), "B", fill="white", font_size=40) # Simple B
    
    return image

def open_dashboard(icon, item):
    """Open the web dashboard."""
    webbrowser.open("http://127.0.0.1:8007")

def toggle_safety(icon, item):
    """Toggle safety mode (via API call essentially)."""
    # Since we are in the same process, we can access the guard directly
    enabled = not local_agent.guard.safe_mode
    local_agent.guard.set_mode(enabled)
    # Update logic for menu item check state would be complex here, 
    # so we rely on the dashboard for detailed status control.
    # Notifications are better.
    icon.notify(f"Safety Mode: {'ON' if enabled else 'OFF'}", "Safety Toggled")

def run_agent_loop():
    """Run the asyncio loop for the agent."""
    global loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(local_agent.main())
    except Exception as e:
        print(f"Agent stopped: {e}")
    finally:
        loop.close()

def quit_app(icon, item):
    """Exit the application."""
    icon.stop()
    print("Exiting...")
    # Stop the asyncio loop
    # We can't easily cancel local_agent's infinite loop from here cleanly without refactoring it to check a flag
    # But os._exit is one way to force kill threads.
    os._exit(0)

def main():
    print("Starting Bridge MCP System Tray...")
    
    # 1. Start Agent in Background Thread
    global agent_thread
    agent_thread = threading.Thread(target=run_agent_loop, daemon=True)
    agent_thread.start()
    
    # 2. Create Tray Icon
    image = create_icon_image()
    menu = pystray.Menu(
        pystray.MenuItem("Open Dashboard", open_dashboard, default=True),
        pystray.MenuItem("Toggle Safety Mode", toggle_safety),
        pystray.MenuItem("Quit", quit_app)
    )
    
    icon = pystray.Icon("Bridge MCP", image, "Bridge MCP Agent", menu)
    
    # Notify user
    # icon.notify("Agent running in background", "Bridge MCP Started") # Some OS dont show this well on start
    
    print("Agent running. Check System Tray.")
    icon.run()

if __name__ == "__main__":
    main()
