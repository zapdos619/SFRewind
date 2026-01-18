"""
Splash Screen for SFRewind
"""
import tkinter as tk
from tkinter import ttk
import base64

class SplashScreen:
    """Splash screen displayed during application startup"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)  # Remove window decorations
        
        # Set size
        width = 500
        height = 400
        
        # Center on screen
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
        # Create main frame with gradient-like background
        self.main_frame = tk.Frame(self.root, bg='#00A1E0', bd=2, relief='solid')
        self.main_frame.pack(fill='both', expand=True)
        
        # Icon placeholder (Salesforce cloud-like design)
        icon_frame = tk.Frame(self.main_frame, bg='#00A1E0')
        icon_frame.pack(pady=40)
        
        # Create simple icon using text
        icon_label = tk.Label(
            icon_frame,
            text="⟲",  # Circular arrow for "rewind"
            font=('Arial', 80, 'bold'),
            fg='white',
            bg='#00A1E0'
        )
        icon_label.pack()
        
        # App name
        name_label = tk.Label(
            self.main_frame,
            text="SFRewind",
            font=('Arial', 28, 'bold'),
            fg='white',
            bg='#00A1E0'
        )
        name_label.pack(pady=10)
        
        # Tagline
        tagline_label = tk.Label(
            self.main_frame,
            text="Salesforce Sandbox Backup & Restore",
            font=('Arial', 11),
            fg='#E0F4FF',
            bg='#00A1E0'
        )
        tagline_label.pack()
        
        # Loading message
        self.status_label = tk.Label(
            self.main_frame,
            text="Loading...",
            font=('Arial', 10),
            fg='white',
            bg='#00A1E0'
        )
        self.status_label.pack(pady=30)
        
        # Progress bar
        self.progress = ttk.Progressbar(
            self.main_frame,
            mode='indeterminate',
            length=300
        )
        self.progress.pack(pady=10)
        self.progress.start(10)
        
        # Version
        version_label = tk.Label(
            self.main_frame,
            text="v1.0.0",
            font=('Arial', 8),
            fg='#E0F4FF',
            bg='#00A1E0'
        )
        version_label.pack(side='bottom', pady=10)
        
        self.root.update()
    
    def update_status(self, message):
        """Update status message"""
        self.status_label.config(text=message)
        self.root.update()
    
    def close(self):
        """Close splash screen"""
        self.progress.stop()
        self.root.destroy()