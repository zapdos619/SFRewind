"""
Main UI Window - PRODUCTION READY
Theme Support + Window Centering Fix
Issue #15 Fixed: Proper window centering on multi-monitor setups
"""
import tkinter as tk
from tkinter import ttk, messagebox
import logging
from ui.login_frame import LoginFrame
from ui.backup_frame import BackupFrame
from ui.restore_frame import RestoreFrame
from config.settings import APP_NAME, APP_VERSION, WINDOW_WIDTH, WINDOW_HEIGHT

logger = logging.getLogger(__name__)

class SalesforceBackupUI:
    """Main application window"""
    
    def __init__(self, root, theme_manager):
        self.root = root
        self.theme_manager = theme_manager
        self.colors = theme_manager.colors
        
        self.root.title(f"{APP_NAME} v{APP_VERSION}")
        
        # Set minimum window size
        self.root.minsize(900, 650)
        
        # Issue #15 Fix: Set window size first, center later
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        
        # Salesforce connection
        self.sf_auth = None
        
        # Setup UI
        self.setup_ui()
        
        # Issue #15 Fix: Center window after UI is ready
        self.center_window()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def center_window(self):
        """Center window on screen (Issue #15 Fix)"""
        # Update window to get actual size
        self.root.update_idletasks()
        
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Get window dimensions
        window_width = self.root.winfo_reqwidth()
        window_height = self.root.winfo_reqheight()
        
        # Calculate center position
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        # Set position
        self.root.geometry(f"+{x}+{y}")
    
    def setup_ui(self):
        """Setup main UI components"""
        # Create notebook (tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Login Tab
        self.login_frame = LoginFrame(self.notebook, self.on_login_success, self.theme_manager)
        self.notebook.add(self.login_frame, text="ðŸ” Login")
        
        # Backup Tab
        self.backup_frame = BackupFrame(self.notebook, self.get_sf_connection, self.handle_logout, self.theme_manager)
        self.notebook.add(self.backup_frame, text="ðŸ’¾ Backup", state='disabled')
        
        # Restore Tab
        self.restore_frame = RestoreFrame(self.notebook, self.get_sf_connection, self.handle_logout, self.theme_manager)
        self.notebook.add(self.restore_frame, text="â™»ï¸ Restore", state='disabled')
        
        # Status Bar
        self.status_bar = ttk.Label(
            self.root,
            text="Not connected - Please login to Salesforce",
            relief=tk.SUNKEN,
            anchor=tk.W,
            padding=(5, 2)
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Apply theme to status bar
        self.theme_manager.configure_widget(self.status_bar, 'status')
    
    def on_login_success(self, sf_auth):
        """Handle successful login"""
        self.sf_auth = sf_auth
        
        # Enable other tabs
        self.notebook.tab(1, state='normal')  # Backup tab
        self.notebook.tab(2, state='normal')  # Restore tab
        
        # Update status
        org_info = sf_auth.org_info
        
        if org_info.get('is_custom_domain'):
            env_type = f"Custom Domain ({org_info['domain']})"
        else:
            env_type = "Sandbox" if org_info['domain'] == 'test' else "Production"
        
        api_version = org_info.get('api_version', 'Unknown')
        
        self.status_bar.config(
            text=f"âœ“ Connected to {env_type} | {org_info['username']} | Org: {org_info['org_id']} | API: v{api_version}"
        )
        
        # Switch to backup tab
        self.notebook.select(1)
        
        messagebox.showinfo(
            "Connection Successful", 
            f"Successfully connected to Salesforce!\n\n"
            f"Environment: {env_type}\n"
            f"Org ID: {org_info['org_id']}\n"
            f"API Version: v{api_version}"
        )
    
    def get_sf_connection(self):
        """Get current Salesforce connection"""
        if self.sf_auth and self.sf_auth.test_connection():
            return self.sf_auth.connection
        else:
            messagebox.showwarning(
                "Not Connected",
                "Your Salesforce session has expired or you're not connected.\n\nPlease login again."
            )
            self.handle_logout()
            return None
    
    def handle_logout(self):
        """Handle logout from Backup/Restore frames"""
        if self.sf_auth:
            self.sf_auth.disconnect()
            self.sf_auth = None
        
        # Disable backup and restore tabs
        self.notebook.tab(1, state='disabled')
        self.notebook.tab(2, state='disabled')
        
        # Switch to login tab
        self.notebook.select(0)
        
        # Update status bar
        self.status_bar.config(text="Logged out - Please login to Salesforce")
        
        messagebox.showinfo("Logged Out", "You have been logged out from Salesforce.")
    
    def on_closing(self):
        """Handle window close event"""
        if self.sf_auth:
            response = messagebox.askyesno(
                "Confirm Exit",
                "Are you sure you want to exit SFRewind?"
            )
            if response:
                self.sf_auth.disconnect()
                self.root.destroy()
        else:
            self.root.destroy()