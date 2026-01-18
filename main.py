"""
SFRewind - Salesforce Sandbox Backup & Restore Tool
Main Entry Point with Splash Screen
"""
import tkinter as tk
from utils.splash_screen import SplashScreen
from utils.theme_manager import ThemeManager
from ui.main_window import SalesforceBackupUI
import time

def main():
    """Main entry point for the application"""
    # Show splash screen
    splash = SplashScreen()
    splash.update_status("Initializing SFRewind...")
    time.sleep(0.5)
    
    splash.update_status("Detecting system theme...")
    time.sleep(0.3)
    
    # Detect theme
    theme_manager = ThemeManager()
    
    splash.update_status("Loading components...")
    time.sleep(0.3)
    
    # Create main window (hidden initially)
    root = tk.Tk()
    root.withdraw()  # Hide window initially
    
    splash.update_status("Applying theme...")
    time.sleep(0.2)
    
    # Apply theme
    theme_manager.apply_theme(root)
    
    splash.update_status("Starting application...")
    time.sleep(0.3)
    
    # Create app
    app = SalesforceBackupUI(root, theme_manager)
    
    # Close splash and show main window
    splash.close()
    root.deiconify()  # Show window
    
    # Start main loop
    root.mainloop()

if __name__ == "__main__":
    main()