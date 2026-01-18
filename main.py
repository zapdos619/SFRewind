"""
SFRewind - Salesforce Sandbox Backup & Restore Tool
Main Entry Point with Splash Screen and Logging
"""
import tkinter as tk
from utils.splash_screen import SplashScreen
from utils.theme_manager import ThemeManager
from ui.main_window import SalesforceBackupUI
import time
import logging
from logging.handlers import RotatingFileHandler
from config.settings import LOGS_DIR, LOG_LEVEL, LOG_FORMAT, APP_NAME, APP_VERSION
from datetime import datetime


def setup_logging():
    """
    Configure application logging (Issue #26 Fix)
    Creates both file and console handlers for comprehensive logging
    """
    # Create logs directory
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, LOG_LEVEL))
    
    # Remove any existing handlers
    logger.handlers = []
    
    # File handler - rotating log file (10MB max, keep 5 backups)
    log_file = LOGS_DIR / f"sfrewind_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10 MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(LOG_FORMAT)
    file_handler.setFormatter(file_formatter)
    
    # Console handler - for development and debugging
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(console_formatter)
    
    # Add handlers to root logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # Log startup information
    logger.info("=" * 60)
    logger.info(f"{APP_NAME} v{APP_VERSION} - Started")
    logger.info(f"Log file: {log_file}")
    logger.info(f"Log level: {LOG_LEVEL}")
    logger.info("=" * 60)
    
    return logger


def main():
    """Main entry point for the application"""
    # Setup logging FIRST (Issue #26 Fix)
    logger = setup_logging()
    
    try:
        logger.info("Initializing application...")
        
        # Show splash screen
        splash = SplashScreen()
        splash.update_status("Initializing SFRewind...")
        time.sleep(0.5)
        
        splash.update_status("Detecting system theme...")
        time.sleep(0.3)
        logger.debug("Detecting system theme...")
        
        # Detect theme
        theme_manager = ThemeManager()
        logger.info(f"Theme detected: {'Dark' if theme_manager.is_dark_mode else 'Light'}")
        
        splash.update_status("Loading components...")
        time.sleep(0.3)
        
        # Create main window (hidden initially)
        root = tk.Tk()
        root.withdraw()  # Hide window initially
        logger.debug("Main window created")
        
        splash.update_status("Applying theme...")
        time.sleep(0.2)
        
        # Apply theme
        theme_manager.apply_theme(root)
        logger.debug("Theme applied to UI")
        
        splash.update_status("Starting application...")
        time.sleep(0.3)
        
        # Create app
        logger.debug("Creating main application UI...")
        app = SalesforceBackupUI(root, theme_manager)
        
        # Close splash and show main window
        splash.close()
        root.deiconify()  # Show window
        logger.info("Application UI ready")
        
        # Start main loop
        logger.info("Starting main event loop")
        root.mainloop()
        
    except Exception as e:
        logger.critical(f"Fatal error during startup: {e}", exc_info=True)
        # Try to show error dialog
        try:
            from tkinter import messagebox
            messagebox.showerror(
                "Startup Error",
                f"Failed to start SFRewind:\n\n{str(e)}\n\nCheck logs for details."
            )
        except:
            pass
        raise
    finally:
        logger.info("Application shutting down")
        logger.info("=" * 60)


if __name__ == "__main__":
    main()