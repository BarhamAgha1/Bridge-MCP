"""
Bridge MCP - AI Activity Indicator Overlay
==========================================
A floating liquid-glass overlay that shows AI activity.
"""

import tkinter as tk
from tkinter import ttk
import threading
import queue
import time
from typing import Optional, Callable
import ctypes
import math

# Enable DPI awareness for crisp rendering
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except:
    pass


class AIOverlay:
    """
    Floating overlay that shows AI activity status.
    Features:
    - Liquid Glassmorphism design
    - Real-time activity display
    - Stop button to interrupt AI
    - Auto-hide when idle
    - Transparent window
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
        self.progress_canvas = None
        self.approval_frame = None
        self.pending_request_id = None
        
        # Colors - Liquid Glass Theme
        self.colors = {
            'bg': '#0a0a0f',       # Deep void black-blue
            'bg_alpha': 0.80,      # High transparency
            'accent_1': '#00f2fe', # Cyan
            'accent_2': '#4facfe', # Blue
            'text': '#ffffff',
            'text_dim': '#8b9bb4',
            'warning': '#ff6b6b',
            'success': '#00ff9d',  # Neon green
            'glass_border': '#2a2a35',
            'glass_shine': '#ffffff'
        }
        
        # Animation state
        self.anim_phase = 0
    
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
        
        # Start loops
        self._check_activity()
        self._animate()
        
        self.root.mainloop()
    
    def _setup_window(self):
        """Configure the main window."""
        self.root.title("Bridge MCP")
        self.root.overrideredirect(True)  # Remove window decorations
        self.root.attributes('-topmost', True)  # Always on top
        self.root.attributes('-alpha', self.colors['bg_alpha'])  # Transparency
        
        # Set window size
        self.window_width = 340
        self.window_height = 130 # Slightly compact
        self.root.geometry(f"{self.window_width}x{self.window_height}")
        
        # Make window draggable
        self.root.bind('<Button-1>', self._start_drag)
        self.root.bind('<B1-Motion>', self._drag_window)
        
        # Background color
        self.root.configure(bg=self.colors['bg'])
    
    def _create_ui(self):
        """Create the UI elements."""
        # Main container with distinct border for glass effect
        # We simulate a border by nesting frames
        border_frame = tk.Frame(
            self.root,
            bg=self.colors['glass_border'],
            padx=1, pady=1
        )
        border_frame.pack(fill='both', expand=True)
        
        main_frame = tk.Frame(
            border_frame,
            bg=self.colors['bg']
        )
        main_frame.pack(fill='both', expand=True)
        
        # Top Bar (Status + Close)
        top_bar = tk.Frame(main_frame, bg=self.colors['bg'])
        top_bar.pack(fill='x', padx=16, pady=(12, 4))
        
        # Status "Pill"
        self.status_pill = tk.Label(
            top_bar,
            text="AI ACTIVE",
            font=('Segoe UI', 8, 'bold'),
            fg=self.colors['accent_1'],
            bg=self.colors['bg']
        )
        self.status_pill.pack(side='left')
        
        # Close Button
        close_btn = tk.Label(
            top_bar,
            text="✕",
            font=('Segoe UI', 9),
            fg=self.colors['text_dim'],
            bg=self.colors['bg'],
            cursor='hand2'
        )
        close_btn.pack(side='right')
        close_btn.bind('<Button-1>', lambda e: self._minimize())
        
        # Main Action Area
        action_container = tk.Frame(main_frame, bg=self.colors['bg'])
        action_container.pack(fill='x', padx=16, pady=4)
        
        self.action_label = tk.Label(
            action_container,
            text="Initializing...",
            font=('Segoe UI', 11),
            fg=self.colors['text'],
            bg=self.colors['bg'],
            anchor='w',
            width=30
        )
        self.action_label.pack(fill='x')
        
        # Fluid Progress Bar
        self.progress_canvas = tk.Canvas(
            main_frame,
            width=300,
            height=4,
            bg='#151520',
            highlightthickness=0
        )
        self.progress_canvas.pack(fill='x', padx=16, pady=(8, 8))
        
        # Bottom Controls
        bottom_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        bottom_frame.pack(fill='x', padx=16, pady=(0, 12))
        
        # Warning/Info Text
        self.info_label = tk.Label(
            bottom_frame,
            text="AI is controlling your mouse",
            font=('Segoe UI', 8),
            fg=self.colors['text_dim'],
            bg=self.colors['bg']
        )
        self.info_label.pack(side='left')
        
        # Stop Button (Pill shaped)
        self.stop_button = tk.Label(
            bottom_frame,
            text="STOP",
            font=('Segoe UI', 8, 'bold'),
            fg='#000000',
            bg=self.colors['warning'],
            padx=12,
            pady=3,
            cursor='hand2'
        )
        self.stop_button.pack(side='right')
        self.stop_button.bind('<Button-1>', self._on_stop_clicked)
        
        # Approval Frame (Hidden Overlay)
        self.approval_frame = tk.Frame(main_frame, bg='#1a1a2e')
        # We'll pack this over everything when needed
        
        self.approval_label = tk.Label(
            self.approval_frame,
            text="Approve Command?",
            font=('Segoe UI', 10, 'bold'),
            fg='white',
            bg='#1a1a2e'
        )
        self.approval_label.pack(pady=(10, 5))
        
        self.approval_cmd = tk.Label(
            self.approval_frame,
            text="...",
            font=('Consolas', 9),
            fg='#a0aec0',
            bg='#1a1a2e',
            wraplength=300
        )
        self.approval_cmd.pack(pady=5)
        
        btn_row = tk.Frame(self.approval_frame, bg='#1a1a2e')
        btn_row.pack(pady=10)
        
        tk.Button(btn_row, text="Approve", bg=self.colors['success'], 
                 command=lambda: self._on_approve_clicked(None)).pack(side='left', padx=5)
        tk.Button(btn_row, text="Deny", bg=self.colors['warning'], 
                 command=lambda: self._on_deny_clicked(None)).pack(side='left', padx=5)

    def _animate(self):
        """Handle animations."""
        if not self.is_running:
            return
            
        self.anim_phase += 0.05
        
        # Animate progress bar (Calm Flow)
        if self.progress_canvas:
            w = self.root.winfo_width() - 32
            self.progress_canvas.delete('all')
            
            # Draw bg
            self.progress_canvas.create_rectangle(0, 0, w, 4, fill='#1a1a25', width=0)
            
            # Calm unidirectional flow (Left to Right)
            # Cycle length = 10 units of phase
            progress = (self.anim_phase % 10) / 10 
            
            center = progress * (w + 100) - 50 # Start before, end after
            width = 80 # Constant width, stable
            
            x1 = center - width/2
            x2 = center + width/2
            
            # Main beam
            self.progress_canvas.create_rectangle(
                max(0, x1), 0, min(w, x2), 4,
                fill=self.colors['accent_1'],
                width=0
            )

        # Pulse status text color
        if self.status_label:
            pass # Tkinter color transition is expensive, skip for now
            
        self.root.after(30, self._animate)

    def _position_window(self):
        """Position window at bottom-right of screen."""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        x = screen_width - self.window_width - 30
        y = screen_height - self.window_height - 60
        
        self.root.geometry(f"{self.window_width}x{self.window_height}+{x}+{y}")
    
    def _start_drag(self, event):
        self.drag_x = event.x
        self.drag_y = event.y
    
    def _drag_window(self, event):
        x = self.root.winfo_x() + event.x - self.drag_x
        y = self.root.winfo_y() + event.y - self.drag_y
        self.root.geometry(f"+{x}+{y}")
    
    def _minimize(self):
        self.root.withdraw()
        self.is_visible = False
        self.root.after(2000, self._check_show_again)
    
    def _check_show_again(self):
        if self.is_running and not self.is_visible:
            self.root.deiconify()
            self.is_visible = True
            
    def _on_stop_clicked(self, event):
        self.stop_requested = True
        self.stop_button.config(text="STOPPING...", bg='#555')
        if self.stop_callback:
            self.stop_callback()
        self.update_action("Stop requested...")
        
    def _check_activity(self):
        if not self.is_running: return
        try:
            while not self.activity_queue.empty():
                action = self.activity_queue.get_nowait()
                self._update_action_ui(action)
        except: pass
        self.root.after(100, self._check_activity)
        
    def _update_action_ui(self, action: str):
        if self.action_label:
            if len(action) > 40: action = action[:37] + "..."
            self.action_label.config(text=action)
            
    # Public API
    def show(self):
        if self.root and not self.is_visible:
            self.root.deiconify()
            self.is_visible = True
            
    def hide(self):
        if self.root and self.is_visible:
            self.root.withdraw()
            self.is_visible = False
            
    def update_action(self, action: str):
        self.activity_queue.put(action)
        
    def set_stop_callback(self, callback: Callable):
        self.stop_callback = callback
        
    def is_stop_requested(self) -> bool:
        return self.stop_requested
        
    def reset_stop(self):
        self.stop_requested = False
        if self.stop_button:
            self.stop_button.config(text="STOP", bg=self.colors['warning'])
            
    def show_approval_request(self, request_id: str, command: str, params: dict):
        self.pending_request_id = request_id
        if self.approval_frame:
            self.approval_cmd.config(text=f"{command}")
            self.approval_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
            
    def hide_approval_request(self):
        if self.approval_frame:
            self.approval_frame.place_forget()
            self.pending_request_id = None

    def _on_approve_clicked(self, event):
        if self.pending_request_id:
            import requests
            try: requests.post('http://127.0.0.1:8006/safety/approve', json={'id': self.pending_request_id}, timeout=1)
            except: pass
            self.hide_approval_request()
            
    def _on_deny_clicked(self, event):
        if self.pending_request_id:
            import requests
            try: requests.post('http://127.0.0.1:8006/safety/deny', json={'id': self.pending_request_id}, timeout=1)
            except: pass
            self.hide_approval_request()
            
    def set_idle(self):
        self.status_pill.config(text="AI IDLE", fg=self.colors['text_dim'])
        self.info_label.config(text="Waiting for tasks...")
        
    def set_active(self):
        self.status_pill.config(text="AI ACTIVE", fg=self.colors['accent_1'])
        self.info_label.config(text="AI is controlling your mouse")

# Global overlay instance
_overlay: Optional[AIOverlay] = None

def get_overlay() -> AIOverlay:
    global _overlay
    if _overlay is None:
        _overlay = AIOverlay()
    return _overlay

def start_overlay():
    overlay = get_overlay()
    overlay.start()
    return overlay

def show_action(action: str):
    overlay = get_overlay()
    overlay.set_active()
    overlay.update_action(action)

def show_approval_request(request_id: str, command: str, params: dict):
    get_overlay().show_approval_request(request_id, command, params)

def hide_approval_request():
    get_overlay().hide_approval_request()

def is_stopped() -> bool:
    return get_overlay().is_stop_requested()

def reset_stop():
    get_overlay().reset_stop()

if __name__ == "__main__":
    overlay = start_overlay()
    import time
    time.sleep(1)
    
    actions = [
        "Scanning screen buffer...",
        "Identifying UI elements...",
        "Calculating cursor trajectory...",
        "Moving to button...",
        "Clicking 'Submit'...",
        "Waiting for page load..."
    ]
    
    for action in actions:
        if is_stopped(): break
        show_action(action)
        time.sleep(2)
        
    overlay.stop()
