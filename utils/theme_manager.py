"""
Theme Manager - Detects system theme and applies colors
"""
import tkinter as tk
from tkinter import ttk
import platform
import subprocess

class ThemeManager:
    """Manages application theme based on system preferences"""
    
    def __init__(self):
        self.is_dark_mode = self.detect_system_theme()
        self.colors = self.get_theme_colors()
    
    def detect_system_theme(self):
        """Detect if system is using dark mode"""
        system = platform.system()
        
        try:
            if system == "Windows":
                # Windows 10/11 dark mode detection
                import winreg
                try:
                    registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
                    key = winreg.OpenKey(registry, r'Software\Microsoft\Windows\CurrentVersion\Themes\Personalize')
                    value, _ = winreg.QueryValueEx(key, 'AppsUseLightTheme')
                    winreg.CloseKey(key)
                    return value == 0  # 0 = Dark mode, 1 = Light mode
                except:
                    return False
            
            elif system == "Darwin":  # macOS
                try:
                    result = subprocess.run(
                        ['defaults', 'read', '-g', 'AppleInterfaceStyle'],
                        capture_output=True,
                        text=True
                    )
                    return 'Dark' in result.stdout
                except:
                    return False
            
            elif system == "Linux":
                # Try to detect GTK theme
                try:
                    result = subprocess.run(
                        ['gsettings', 'get', 'org.gnome.desktop.interface', 'gtk-theme'],
                        capture_output=True,
                        text=True
                    )
                    return 'dark' in result.stdout.lower()
                except:
                    return False
        except:
            pass
        
        return False  # Default to light mode
    
    def get_theme_colors(self):
        """Get color scheme based on theme"""
        if self.is_dark_mode:
            return {
                # Dark theme colors
                'bg': '#1E1E1E',           # Main background
                'fg': '#E0E0E0',           # Main text
                'bg_secondary': '#2D2D2D', # Secondary background
                'fg_secondary': '#B0B0B0', # Secondary text
                'accent': '#00A1E0',       # Salesforce blue
                'button_bg': '#0D47A1',    # Button background
                'button_fg': '#FFFFFF',    # Button text
                'entry_bg': '#2D2D2D',     # Input background
                'entry_fg': '#E0E0E0',     # Input text
                'frame_bg': '#252525',     # Frame background
                'selected_bg': '#0D47A1',  # Selected item
                'border': '#3D3D3D',       # Border color
                'success': '#4CAF50',      # Success green
                'error': '#F44336',        # Error red
                'warning': '#FF9800',      # Warning orange
            }
        else:
            return {
                # Light theme colors
                'bg': '#FFFFFF',           # Main background
                'fg': '#000000',           # Main text
                'bg_secondary': '#F5F5F5', # Secondary background
                'fg_secondary': '#666666', # Secondary text
                'accent': '#00A1E0',       # Salesforce blue
                'button_bg': '#00A1E0',    # Button background
                'button_fg': '#FFFFFF',    # Button text
                'entry_bg': '#FFFFFF',     # Input background
                'entry_fg': '#000000',     # Input text
                'frame_bg': '#FAFAFA',     # Frame background
                'selected_bg': '#00A1E0',  # Selected item
                'border': '#DDDDDD',       # Border color
                'success': '#4CAF50',      # Success green
                'error': '#F44336',        # Error red
                'warning': '#FF9800',      # Warning orange
            }
    
    def apply_theme(self, root):
        """Apply theme to the application"""
        colors = self.colors
        
        # Configure root window
        root.configure(bg=colors['bg'])
        
        # Configure ttk style
        style = ttk.Style()
        
        # Try to use a modern theme as base
        available_themes = style.theme_names()
        if self.is_dark_mode:
            # For dark mode, use clam as base (most customizable)
            if 'clam' in available_themes:
                style.theme_use('clam')
        else:
            # For light mode, use default or vista
            if 'vista' in available_themes:
                style.theme_use('vista')
            elif 'clam' in available_themes:
                style.theme_use('clam')
        
        # Configure ttk widgets
        style.configure('TFrame', background=colors['bg'])
        style.configure('TLabel', background=colors['bg'], foreground=colors['fg'])
        style.configure('TButton', background=colors['button_bg'], foreground=colors['button_fg'])
        style.configure('TEntry', fieldbackground=colors['entry_bg'], foreground=colors['entry_fg'])
        style.configure('TLabelframe', background=colors['bg'], foreground=colors['fg'])
        style.configure('TLabelframe.Label', background=colors['bg'], foreground=colors['fg'])
        style.configure('TNotebook', background=colors['bg'])
        style.configure('TNotebook.Tab', background=colors['bg_secondary'], foreground=colors['fg'])
        
        # Listbox colors
        style.map('TButton',
            background=[('active', colors['accent'])],
            foreground=[('active', colors['button_fg'])]
        )
        
        return colors
    
    def configure_widget(self, widget, widget_type='frame'):
        """Configure individual widget colors"""
        colors = self.colors
        
        if isinstance(widget, tk.Text):
            widget.configure(
                bg=colors['entry_bg'],
                fg=colors['entry_fg'],
                insertbackground=colors['fg'],
                selectbackground=colors['selected_bg'],
                selectforeground=colors['button_fg']
            )
        elif isinstance(widget, tk.Listbox):
            widget.configure(
                bg=colors['entry_bg'],
                fg=colors['entry_fg'],
                selectbackground=colors['selected_bg'],
                selectforeground=colors['button_fg']
            )
        elif isinstance(widget, tk.Entry):
            widget.configure(
                bg=colors['entry_bg'],
                fg=colors['entry_fg'],
                insertbackground=colors['fg']
            )
        elif isinstance(widget, tk.Label):
            if widget_type == 'status':
                widget.configure(bg=colors['bg_secondary'], fg=colors['fg'])
            else:
                widget.configure(bg=colors['bg'], fg=colors['fg'])
        elif isinstance(widget, tk.Frame):
            widget.configure(bg=colors['bg'])