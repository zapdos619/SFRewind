"""
Configuration settings for SFRewind
Issue #29 Fix: All magic numbers now defined as named constants
"""
import os
from pathlib import Path

# Application Settings
APP_NAME = "SFRewind"
APP_VERSION = "2.0.0"  # Updated to reflect all fixes

# File Storage Settings
BASE_DIR = Path.home() / "SFRewind"
BACKUP_DIR = BASE_DIR / "backups"
CONFIG_DIR = BASE_DIR / "configs"
LOGS_DIR = BASE_DIR / "logs"

# Ensure directories exist
for directory in [BASE_DIR, BACKUP_DIR, CONFIG_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Salesforce API Settings
API_VERSION = "59.0"
BULK_API_BATCH_SIZE = 10000
DEFAULT_BATCH_SIZE = 200  # Issue #29: Salesforce API works well with 200-2000
MIN_BATCH_SIZE = 1
MAX_BATCH_SIZE = 10000

# File Format Settings
EXPORT_FORMAT = "csv"  # Options: csv, excel
DATE_FORMAT = "%Y%m%d_%H%M%S"

# UI Settings
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 700
WINDOW_MIN_WIDTH = 900  # Issue #29: Minimum window size
WINDOW_MIN_HEIGHT = 650
THEME_COLOR = "#00A1E0"  # Salesforce blue

# UI Component Sizes (Issue #29 Fix)
AVAILABLE_OBJECTS_CANVAS_HEIGHT = 120  # pixels
OBJECT_BUTTON_WIDTH = 15  # characters
MAX_PROGRESS_TEXT_LENGTH = 50  # characters
LISTBOX_DEFAULT_HEIGHT = 10  # rows
TEXT_WIDGET_HEIGHT = 10  # rows
RESULTS_TEXT_WIDTH = 40  # characters

# Splash Screen Settings (Issue #29 Fix)
SPLASH_SCREEN_MIN_DISPLAY_TIME = 0.5  # seconds per step
SPLASH_SCREEN_WIDTH = 500  # pixels
SPLASH_SCREEN_HEIGHT = 400  # pixels

# Validation Constants (Issue #29 Fix)
SALESFORCE_TOKEN_MIN_LENGTH = 24  # Salesforce security tokens are 24-25 chars
SALESFORCE_TOKEN_MAX_LENGTH = 25
MIN_PASSWORD_LENGTH = 8  # Minimum recommended password length
MAX_BACKUP_NAME_LENGTH = 100  # characters

# Timeout Constants (Issue #29 Fix)
CONNECTION_TIMEOUT_SECONDS = 30  # Salesforce connection timeout
API_CALL_TIMEOUT_SECONDS = 60  # Individual API call timeout
SESSION_TIMEOUT_SECONDS = 7200  # 2 hours = Salesforce session duration
SESSION_REFRESH_BUFFER_SECONDS = 300  # 5 minutes before expiry

# Thread and Operation Settings (Issue #29 Fix)
MAX_RECONNECT_ATTEMPTS = 3  # Maximum times to retry connection
RETRY_BACKOFF_BASE = 2  # Exponential backoff base (1s, 2s, 4s)
PROGRESS_LOG_INTERVAL = 10000  # Log progress every N records
THREAD_CLEANUP_TIMEOUT = 5.0  # Seconds to wait for thread cleanup

# Logging Settings
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE_MAX_BYTES = 10 * 1024 * 1024  # 10 MB
LOG_FILE_BACKUP_COUNT = 5  # Keep 5 backup log files

# Cache Settings (Issue #29 Fix)
ENABLE_METADATA_CACHE = True  # Enable/disable metadata caching
CACHE_INVALIDATION_TIME = 3600  # Seconds before cache expires (1 hour)

# Progress Bar Settings (Issue #14 Fix)
PROGRESS_BAR_MODE = 'determinate'  # 'determinate' or 'indeterminate'
PROGRESS_BAR_UPDATE_INTERVAL = 100  # Milliseconds between updates