"""
Configuration settings for SFRewind
"""
import os
from pathlib import Path

# Application Settings
APP_NAME = "SFRewind"
APP_VERSION = "1.0.0"

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

# File Format Settings
EXPORT_FORMAT = "csv"  # Options: csv, excel
DATE_FORMAT = "%Y%m%d_%H%M%S"

# UI Settings
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 700
THEME_COLOR = "#00A1E0"  # Salesforce blue

# Logging Settings
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"