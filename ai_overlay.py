"""
Bridge MCP - AI Activity Indicator Overlay
==========================================
A floating glassmorphism overlay that shows AI activity and allows user interruption.
"""

import tkinter as tk
from tkinter import ttk
import threading
import queue
import time
from typing import Optional, Callable
import ctypes

# Enable DPI awareness for crisp rendering
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except:
    pass


class AIOverlay:
    """
    Floating overlay that shows AI activity status.
    Features:
    - Glassmorphism design
    - Real-time activity display
    - Stop button to interrupt AI
    - Auto-hide when idle
    """
    
    def __init__(self):
        self.root: Optional[tk.Tk] = None
        self.is_running = False
        self.is_visible = False
        self.activity_queue = queue.Queue()
        self.stop_callback: Optional[Callable] = None
        self.stop_requested = False
        self._thread: Optional[threading.Thread] = None
        
        # UI Elements
        self.status_label = None
        self.action_label = None
        self.stop_button = None
        self.progress_bar = None
        
        # Colors - Glassmorphism theme
        self.colors = {
            'bg': '#1a1a2e',
            'bg_alpha': 0.85,
            'accent': '#4facfe',
            'accent_hover': '#00f2fe',
            'text': '#ffffff',
            'text_dim': '#a0a0a0',
            'warning': '#ff6b6b',
            'success': '#4ade80',
            'glass_border': '#e0e0e0'
        }
    
    def start(self):
        """Start the overlay in a separate thread."""
        if self.is_running:
            return
        
        self.is_running = True
        self.stop_requested = False
        self._thread = threading.Thread(target=self._run_overlay, daemon=True)
        self._thread.start()
    
    def stop(self):
        """Stop the overlay."""
        self.is_running = False
        if self.root:
            try:
                self.root.quit()
            except:
                pass
    
    def _run_overlay(self):
        """Main overlay loop."""
        self.root = tk.Tk()
        self._setup_window()
        self._create_ui()
        self._position_window()
        
        # Start activity checker
        self._check_activity()
        
        self.root.mainloop()
    
    def _setup_window(self):
        """Configure the main window."""
        self.root.title("Bridge MCP")
        self.root.overrideredirect(True)  # Remove window decorations
        self.root.attributes('-topmost', True)  # Always on top
        self.root.attributes('-alpha', self.colors['bg_alpha'])  # Transparency
        
        # Set window size
        self.window_width = 320
        self.window_height = 140
        self.root.geometry(f"{self.window_width}x{self.window_height}")
        
        # Make window draggable
        self.root.bind('<Button-1>', self._start_drag)
        self.root.bind('<B1-Motion>', self._drag_window)
        
        # Background color
        self.root.configure(bg=self.colors['bg'])
    
    def _create_ui(self):
        """Create the UI elements."""
        # Main container with rounded corners effect
        main_frame = tk.Frame(
            self.root,
            bg=self.colors['bg'],
            highlightbackground=self.colors['glass_border'],
            highlightthickness=1
        )
        main_frame.pack(fill='both', expand=True, padx=2, pady=2)
        
        # Header with AI icon and status
        header_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        header_frame.pack(fill='x', padx=15, pady=(12, 5))
        
        # AI Status indicator (pulsing dot + text)
        self.status_dot = tk.Canvas(
            header_frame, 
            width=12, 
            height=12, 
            bg=self.colors['bg'],
            highlightthickness=0
        )
        self.status_dot.pack(side='left')
        self._draw_status_dot('active')
        
        self.status_label = tk.Label(
            header_frame,
            text="AI IS CONTROLLING YOUR PC",
            font=('Segoe UI', 9, 'bold'),
            fg=self.colors['accent'],
            bg=self.colors['bg']
        )
        self.status_label.pack(side='left', padx=(8, 0))
        
        # Close/minimize button
        close_btn = tk.Label(
            header_frame,
            text="—",
            font=('Segoe UI', 12),
            fg=self.colors['text_dim'],
            bg=self.colors['bg'],
            cursor='hand2'
        )
        close_btn.pack(side='right')
        close_btn.bind('<Button-1>', lambda e: self._minimize())
        close_btn.bind('<Enter>', lambda e: close_btn.config(fg=self.colors['text']))
        close_btn.bind('<Leave>', lambda e: close_btn.config(fg=self.colors['text_dim']))
        
        # Divider line
        divider = tk.Frame(main_frame, bg=self.colors['glass_border'], height=1)
        divider.pack(fill='x', padx=15, pady=5)
        
        # Current action display
        action_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        action_frame.pack(fill='x', padx=15, pady=5)
        
        action_icon = tk.Label(
            action_frame,
            text="▶",
            font=('Segoe UI', 8),
            fg=self.colors['success'],
            bg=self.colors['bg']
        )
        action_icon.pack(side='left')
        
        self.action_label = tk.Label(
            action_frame,
            text="Waiting for commands...",
            font=('Segoe UI', 10),
            fg=self.colors['text'],
            bg=self.colors['bg'],
            anchor='w'
        )
        self.action_label.pack(side='left', padx=(8, 0), fill='x', expand=True)
        
        # Warning message
        warning_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        warning_frame.pack(fill='x', padx=15, pady=(0, 5))
        
        self.warning_label = tk.Label(
            warning_frame,
            text="⚠ Don't move mouse or type - AI is working",
            font=('Segoe UI', 8),
            fg=self.colors['warning'],
            bg=self.colors['bg']
        )
        self.warning_label.pack(side='left')
        
        # Bottom bar with Stop button
        bottom_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        bottom_frame.pack(fill='x', padx=15, pady=(5, 12))
        
        # Progress indicator (animated)
        self.progress_canvas = tk.Canvas(
            bottom_frame,
            width=150,
            height=3,
            bg=self.colors['bg'],
            highlightthickness=0
        )
        self.progress_canvas.pack(side='left', pady=8)
        self._start_progress_animation()
        
        # Stop button
        self.stop_button = tk.Label(
            bottom_frame,
            text="⏹ STOP",
            font=('Segoe UI', 9, 'bold'),
            fg=self.colors['bg'],
            bg=self.colors['warning'],
            padx=12,
            pady=4,
            cursor='hand2'
        )
        self.stop_button.pack(side='right')
        self.stop_button.bind('<Button-1>', self._on_stop_clicked)
        self.stop_button.bind('<Enter>', lambda e: self.stop_button.config(bg='#ff4757'))
        self.stop_button.bind('<Leave>', lambda e: self.stop_button.config(bg=self.colors['warning']))
    
    def _draw_status_dot(self, status='active'):
        """Draw the status indicator dot."""
        self.status_dot.delete('all')
        color = self.colors['success'] if status == 'active' else self.colors['text_dim']
        self.status_dot.create_oval(2, 2, 10, 10, fill=color, outline=color)
    
    def _start_progress_animation(self):
        """Animate the progress bar."""
        self.progress_pos = 0
        self._animate_progress()
    
    def _animate_progress(self):
        """Progress bar animation loop."""
        if not self.is_running or not self.root:
            return
        
        try:
            self.progress_canvas.delete('all')
            
            # Background
            self.progress_canvas.create_rectangle(
                0, 0, 150, 3,
                fill='#333355',
                outline=''
            )
            
            # Animated segment
            segment_width = 40
            x1 = self.progress_pos
            x2 = min(self.progress_pos + segment_width, 150)
            
            # Create gradient effect
            self.progress_canvas.create_rectangle(
                x1, 0, x2, 3,
                fill=self.colors['accent'],
                outline=''
            )
            
            # Move the segment
            self.progress_pos += 3
            if self.progress_pos > 150:
                self.progress_pos = -segment_width
            
            self.root.after(30, self._animate_progress)
        except:
            pass
    
    def _position_window(self):
        """Position window at bottom-right of screen."""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        x = screen_width - self.window_width - 20
        y = screen_height - self.window_height - 60  # Above taskbar
        
        self.root.geometry(f"{self.window_width}x{self.window_height}+{x}+{y}")
    
    def _start_drag(self, event):
        """Start dragging the window."""
        self.drag_x = event.x
        self.drag_y = event.y
    
    def _drag_window(self, event):
        """Drag the window."""
        x = self.root.winfo_x() + event.x - self.drag_x
        y = self.root.winfo_y() + event.y - self.drag_y
        self.root.geometry(f"+{x}+{y}")
    
    def _minimize(self):
        """Minimize/hide the overlay."""
        self.root.withdraw()
        self.is_visible = False
        
        # Show again after 2 seconds if AI is still active
        self.root.after(2000, self._check_show_again)
    
    def _check_show_again(self):
        """Check if overlay should be shown again."""
        if self.is_running and not self.is_visible:
            self.root.deiconify()
            self.is_visible = True
    
    def _on_stop_clicked(self, event):
        """Handle stop button click."""
        self.stop_requested = True
        self.stop_button.config(text="⏹ STOPPING...", bg=self.colors['text_dim'])
        
        if self.stop_callback:
            self.stop_callback()
        
        self.update_action("Stop requested by user")
        self.warning_label.config(text="✓ AI operations will stop", fg=self.colors['success'])
    
    def _check_activity(self):
        """Check for new activity updates."""
        if not self.is_running:
            return
        
        try:
            while not self.activity_queue.empty():
                action = self.activity_queue.get_nowait()
                self._update_action_ui(action)
        except:
            pass
        
        if self.root:
            self.root.after(100, self._check_activity)
    
    def _update_action_ui(self, action: str):
        """Update the action label."""
        if self.action_label:
            # Truncate long actions
            if len(action) > 35:
                action = action[:32] + "..."
            self.action_label.config(text=action)
    
    # ==========================================
    # PUBLIC API
    # ==========================================
    
    def show(self):
        """Show the overlay."""
        if self.root and not self.is_visible:
            self.root.deiconify()
            self.is_visible = True
    
    def hide(self):
        """Hide the overlay."""
        if self.root and self.is_visible:
            self.root.withdraw()
            self.is_visible = False
    
    def update_action(self, action: str):
        """Update the current action being performed."""
        self.activity_queue.put(action)
    
    def set_stop_callback(self, callback: Callable):
        """Set the callback function for stop button."""
        self.stop_callback = callback
    
    def is_stop_requested(self) -> bool:
        """Check if user requested to stop."""
        return self.stop_requested
    
    def reset_stop(self):
        """Reset the stop request flag."""
        self.stop_requested = False
        if self.stop_button:
            try:
                self.stop_button.config(text="⏹ STOP", bg=self.colors['warning'])
                self.warning_label.config(
                    text="⚠ Don't move mouse or type - AI is working",
                    fg=self.colors['warning']
                )
            except:
                pass
    
    def set_idle(self):
        """Set overlay to idle state."""
        if self.status_label:
            try:
                self.status_label.config(text="AI READY", fg=self.colors['text_dim'])
                self._draw_status_dot('idle')
                self.warning_label.config(text="AI is idle - you can use your PC", fg=self.colors['success'])
            except:
                pass
    
    def set_active(self):
        """Set overlay to active state."""
        if self.status_label:
            try:
                self.status_label.config(text="AI IS CONTROLLING YOUR PC", fg=self.colors['accent'])
                self._draw_status_dot('active')
                self.warning_label.config(
                    text="⚠ Don't move mouse or type - AI is working",
                    fg=self.colors['warning']
                )
            except:
                pass


# Global overlay instance
_overlay: Optional[AIOverlay] = None


def get_overlay() -> AIOverlay:
    """Get or create the global overlay instance."""
    global _overlay
    if _overlay is None:
        _overlay = AIOverlay()
    return _overlay


def start_overlay():
    """Start the overlay."""
    overlay = get_overlay()
    overlay.start()
    return overlay


def show_action(action: str):
    """Show an action in the overlay."""
    overlay = get_overlay()
    overlay.set_active()
    overlay.update_action(action)


def is_stopped() -> bool:
    """Check if user requested stop."""
    overlay = get_overlay()
    return overlay.is_stop_requested()


def reset_stop():
    """Reset stop flag."""
    overlay = get_overlay()
    overlay.reset_stop()


# ==========================================
# TEST
# ==========================================

if __name__ == "__main__":
    # Test the overlay
    overlay = start_overlay()
    
    import time
    time.sleep(1)
    
    # Simulate AI actions
    actions = [
        "Taking screenshot...",
        "Analyzing screen content...",
        "Moving mouse to (450, 320)...",
        "Clicking button 'Submit'...",
        "Typing text: 'Hello World'...",
        "Opening Chrome browser...",
        "Navigating to google.com...",
        "Searching for 'Bridge MCP'...",
    ]
    
    for action in actions:
        if is_stopped():
            print("User stopped the AI!")
            break
        show_action(action)
        time.sleep(2)
    
    overlay.set_idle()
    time.sleep(3)
    overlay.stop()
