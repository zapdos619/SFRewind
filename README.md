# 🔄 SFRewind - Salesforce Sandbox Backup & Restore Tool

**Version 2.0.0** - Production-Ready Edition

A professional, enterprise-grade desktop application for backing up and restoring Salesforce sandbox data with a beautiful UI, comprehensive logging, and bulletproof reliability.

---

## 🌟 Key Features

### 🎯 Core Functionality
- ✅ **Backup Salesforce Data** - Export objects with all fields to CSV
- ✅ **Restore Data** - Import data with dependency resolution
- ✅ **Smart Field Mapping** - Validates fields before import
- ✅ **Relationship Detection** - Automatically detects object dependencies
- ✅ **Checkpoint System** - Resume interrupted restore operations

### 🎨 User Experience
- ✅ **Real-Time Progress** - See exactly what's happening (0% → 100%)
- ✅ **Auto Theme Detection** - Matches your system's dark/light mode
- ✅ **No UI Freezing** - Fully threaded operations
- ✅ **Professional UI** - Clean, modern interface
- ✅ **Multi-Monitor Support** - Perfect window centering

### 🔒 Security & Reliability
- ✅ **Secure Credentials** - Passwords cleared from memory after use
- ✅ **Auto-Reconnect** - Handles session timeouts automatically
- ✅ **Comprehensive Logging** - Full audit trail of all operations
- ✅ **Thread-Safe** - No race conditions or data corruption
- ✅ **Graceful Cancellation** - Stop operations safely anytime

### ⚡ Performance
- ✅ **Metadata Caching** - 20x faster repeated operations
- ✅ **Memory Efficient** - Handles 100k+ records without issues
- ✅ **No File Handle Leaks** - Unlimited operations
- ✅ **Streaming Exports** - Constant memory usage regardless of size

---

## 📋 What's New in v2.0.0

### 🎯 All Critical Issues Fixed (17 Total)

#### Security & Stability (8 Fixes)
1. ✅ **Secure Credential Handling** - Passwords wiped from memory
2. ✅ **Thread Safety** - All shared state protected with locks
3. ✅ **Widget Updates** - All UI updates via `self.after()`
4. ✅ **Race Condition Prevention** - Proper lambda value captures
5. ✅ **Operation Cancellation** - Cancel button works everywhere
6. ✅ **Field Validation** - Prevents data loss on import
7. ✅ **Smart Import Order** - Kahn's algorithm with cycle detection
8. ✅ **Checkpoint System** - Resume failed imports

#### Performance & Reliability (5 Fixes)
9. ✅ **Comprehensive Logging** - Rotating file logs (10MB, 5 backups)
10. ✅ **Auto-Reconnect** - Handles 2-hour session timeouts
11. ✅ **Memory Leak Fix** - Streaming instead of loading all data
12. ✅ **File Handle Leak Fix** - All files use context managers
13. ✅ **Metadata Caching** - Describe calls cached for speed

#### UX Improvements (4 Fixes)
14. ✅ **Real Progress Bars** - Shows 0% → 100% (not spinning)
15. ✅ **Window Centering** - Perfect positioning on multi-monitor setups
16. ✅ **Duplicate Prevention** - Can't add same object twice
17. ✅ **Named Constants** - All magic numbers in settings.py

---

## 🚀 Quick Start

### Prerequisites

**Required:**
- Python 3.7+
- Salesforce Sandbox or Production org
- Security Token (from Salesforce)

**Operating Systems:**
- ✅ Windows 10/11
- ✅ macOS 10.14+
- ✅ Linux (Ubuntu, Fedora, etc.)

### Installation

1. **Install Dependencies**

```bash
pip install simple-salesforce
```

**Windows Users Only:**
```bash
pip install pywin32
```
*Required for dark mode detection via Windows registry*

2. **Download/Clone the Project**

```bash
git clone <your-repo-url>
cd SFRewind
```

3. **Run the Application**

```bash
python main.py
```

---

## 📁 Project Structure

```
SFRewind/
├── main.py                      # 🚀 Entry point with splash screen
├── requirements.txt             # 📦 Dependencies
│
├── config/
│   ├── __init__.py
│   └── settings.py              # ⚙️  All configuration constants
│
├── core/                        # 🔧 Business logic
│   ├── __init__.py
│   ├── salesforce_auth.py       # 🔐 Authentication with auto-reconnect
│   ├── backup_manager.py        # 💾 Backup with streaming & caching
│   └── restore_manager.py       # 📥 Restore with checkpoints & validation
│
├── ui/                          # 🎨 User interface
│   ├── __init__.py
│   ├── main_window.py           # 🪟 Main window with multi-monitor support
│   ├── login_frame.py           # 🔑 Login with secure credential handling
│   ├── backup_frame.py          # 📊 Backup with real-time progress
│   └── restore_frame.py         # 🔄 Restore with checkpoint resume
│
└── utils/                       # 🛠️  Utilities
    ├── __init__.py
    ├── splash_screen.py         # ✨ Professional loading screen
    └── theme_manager.py         # 🎨 Auto dark/light theme detection
```

---

## 💻 Usage Guide

### 1. Login to Salesforce

**Required Information:**
- **Username**: Your Salesforce email (e.g., `user@company.com.sandbox`)
- **Password**: Your Salesforce password
- **Security Token**: Reset from Setup → My Personal Information → Reset Security Token
- **Environment**: Sandbox or Production

**Custom Domain Support:**
- Check "Use Custom Domain" for My Domain setups
- Enter domain like: `mycompany.my.salesforce.com`

### 2. Create a Backup

1. **Select Objects**
   - Click "Load All Objects" to see all available objects
   - Or search for specific objects
   - Click object buttons to add them to backup list

2. **Configure Backup**
   - Choose backup location (default: `~/SFRewind/backups/`)
   - Optionally name your backup
   - Click "Start Backup"

3. **Monitor Progress**
   - Real-time progress bar: `[████░░] 60%`
   - Status updates: `Backed up Account (3/5 objects)`
   - View results when complete

**Backup Output:**
```
~/SFRewind/backups/backup_20250120_143022/
├── metadata.json          # Object definitions & relationships
├── #backuplog.txt         # Detailed operation log
├── Account.csv            # Exported data
├── Contact.csv
├── Opportunity.csv
└── ...
```

### 3. Restore a Backup

1. **Select Backup**
   - Click "Browse..." to choose backup folder
   - Click "Load Backup" to view details

2. **Review & Confirm**
   - Check object list and record counts
   - Confirm restore operation
   - Watch real-time progress

3. **Handle Checkpoints**
   - If restore fails, checkpoint is saved
   - On next attempt, choose to resume from checkpoint
   - Skip already-imported objects automatically

**Restore Output:**
```
~/SFRewind/backups/backup_20250120_143022/
├── #uploadlog.txt         # Detailed restore log
├── .checkpoint.json       # Resume data (if interrupted)
└── ...
```

---

## 🎨 Theme Support

### Automatic Detection

**Windows:**
```
Reads: HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize
Checks: AppsUseLightTheme (0 = Dark, 1 = Light)
```

**macOS:**
```bash
defaults read -g AppleInterfaceStyle
# "Dark" = Dark Mode
```

**Linux:**
```bash
gsettings get org.gnome.desktop.interface gtk-theme
# Contains "dark" = Dark Mode
```

### Color Schemes

**Dark Mode:**
- Background: `#1E1E1E` (Dark Gray)
- Text: `#E0E0E0` (Light Gray)
- Accent: `#00A1E0` (Salesforce Blue)
- Entry Fields: `#2D2D2D` (Darker Gray)

**Light Mode:**
- Background: `#FFFFFF` (White)
- Text: `#000000` (Black)
- Accent: `#00A1E0` (Salesforce Blue)
- Entry Fields: `#FFFFFF` (White)

---

## ⚙️ Configuration

All settings are in `config/settings.py`:

### Application Settings
```python
APP_NAME = "SFRewind"
APP_VERSION = "2.0.0"
```

### File Locations
```python
BASE_DIR = Path.home() / "SFRewind"        # ~/SFRewind/
BACKUP_DIR = BASE_DIR / "backups"          # ~/SFRewind/backups/
LOGS_DIR = BASE_DIR / "logs"               # ~/SFRewind/logs/
```

### Performance Tuning
```python
DEFAULT_BATCH_SIZE = 200                   # Salesforce API batch size
ENABLE_METADATA_CACHE = True               # Cache describe calls
CACHE_INVALIDATION_TIME = 3600             # 1 hour cache
```

### Session Management
```python
SESSION_TIMEOUT_SECONDS = 7200             # 2 hours
SESSION_REFRESH_BUFFER_SECONDS = 300       # 5 min warning
MAX_RECONNECT_ATTEMPTS = 3                 # Auto-reconnect tries
```

### UI Customization
```python
WINDOW_WIDTH = 1000                        # Main window size
WINDOW_HEIGHT = 700
PROGRESS_BAR_MODE = 'determinate'          # Real progress vs spinning
OBJECT_BUTTON_WIDTH = 25                   # Object button size
```

### Logging
```python
LOG_LEVEL = "INFO"                         # DEBUG, INFO, WARNING, ERROR
LOG_FILE_MAX_BYTES = 10 * 1024 * 1024     # 10 MB per file
LOG_FILE_BACKUP_COUNT = 5                  # Keep 5 old logs
```

---

## 📊 Progress Indicators

### Backup Progress
```
[░░░░░░░░░░] 0%    Backing up 0/5 objects...
[██░░░░░░░░] 20%   Backed up Account (1/5 objects)
[████░░░░░░] 40%   Backed up Contact (2/5 objects)
[██████░░░░] 60%   Backed up Opportunity (3/5 objects)
[████████░░] 80%   Backed up Case (4/5 objects)
[██████████] 100%  Backed up Lead (5/5 objects)
```

### Restore Progress
```
[░░░░░░░░░░] 0%    Restoring...
[███░░░░░░░] 30%   Restoring Account...
[██████░░░░] 60%   Restoring Contact...
[██████████] 100%  Restore completed!
```

---

## 🔍 Logging & Troubleshooting

### Log Locations

**Application Logs:**
```
~/SFRewind/logs/sfrewind_20250120.log
```

**Backup Logs:**
```
~/SFRewind/backups/backup_20250120_143022/#backuplog.txt
```

**Restore Logs:**
```
~/SFRewind/backups/backup_20250120_143022/#uploadlog.txt
```

### Log Format
```
2025-01-20 14:30:22,123 - core.backup_manager - INFO - Starting backup: backup_20250120_143022
2025-01-20 14:30:25,456 - core.backup_manager - DEBUG - Starting export of Account with 45 fields
2025-01-20 14:30:28,789 - core.backup_manager - INFO - ✓ Exported 1,234 records from Account
```

### Common Issues

#### Issue: "Invalid Session" Error
**Cause:** Session timeout (2 hours)  
**Fix:** Auto-reconnect is enabled - will reconnect automatically  
**Manual:** Logout and login again

#### Issue: "Field not found" during Restore
**Cause:** Field exists in backup but not in target org  
**Fix:** Field validation automatically skips invalid fields  
**Check:** #uploadlog.txt for skipped fields

#### Issue: UI Freezing
**Cause:** Usually resolved in v2.0.0  
**Fix:** Check if using latest version  
**Debug:** Check logs for long-running operations

#### Issue: Restore Fails Midway
**Cause:** Network issue, API limit, data validation error  
**Fix:** Checkpoint system saves progress  
**Action:** Re-run restore, choose "Resume from checkpoint"

#### Issue: Progress Bar Not Moving
**Cause:** Large objects take time to export  
**Fix:** v2.0.0 shows real-time progress per object  
**Note:** Each object completion updates the bar

---

## 🎯 Best Practices

### Before Backup
1. ✅ **Test connection** - Login and verify objects load
2. ✅ **Choose wisely** - Select only needed objects
3. ✅ **Check space** - Ensure enough disk space
4. ✅ **Name backups** - Use descriptive names for easy identification

### During Backup
1. ✅ **Monitor progress** - Watch status and progress bar
2. ✅ **Don't interrupt** - Let backup complete fully
3. ✅ **Check logs** - Review #backuplog.txt after completion
4. ✅ **Verify data** - Open CSV files to spot-check

### Before Restore
1. ✅ **Verify target** - Confirm you're in the right org
2. ✅ **Check fields** - Ensure target org has same fields
3. ✅ **Review relationships** - Understand dependencies
4. ✅ **Backup first** - Create backup of target org before restoring

### During Restore
1. ✅ **Watch for errors** - Check #uploadlog.txt for failures
2. ✅ **Use checkpoints** - Resume if restore fails
3. ✅ **Validate data** - Verify records after restore
4. ✅ **Check relationships** - Ensure references are correct

---

## ⚡ Performance Tips

### Large Datasets (100k+ Records)
- ✅ Backup/Restore in batches (select fewer objects per operation)
- ✅ Increase `DEFAULT_BATCH_SIZE` in settings.py (up to 2000)
- ✅ Close other applications to free memory
- ✅ Use wired connection instead of WiFi

### Slow Networks
- ✅ Reduce `DEFAULT_BATCH_SIZE` to 100-200
- ✅ Increase `CONNECTION_TIMEOUT_SECONDS` to 60
- ✅ Backup during off-peak hours
- ✅ Monitor progress - slow but steady is normal

### Many Objects (50+)
- ✅ Use "Load All Objects" once, then search
- ✅ Metadata caching speeds up subsequent operations
- ✅ Group related objects in separate backups
- ✅ Clear cache if schema changes: restart app

---

## 🔒 Security Notes

### Credentials
- ✅ **Never stored on disk** - Only in memory during session
- ✅ **Cleared after use** - `SecureString` class wipes memory
- ✅ **No plaintext logs** - Logs don't contain passwords
- ✅ **Session-only** - Re-enter on each app launch

### Security Token
- ✅ **Reset from Salesforce** if compromised
- ✅ **Not shared** - Never share security tokens
- ✅ **Unique per user** - Each user needs their own

### Data Security
- ✅ **Local storage** - Backups stored locally on your machine
- ✅ **CSV format** - Human-readable, can be encrypted separately
- ✅ **Access control** - OS file permissions apply
- ✅ **Audit trail** - All operations logged

---

## 🧪 Testing Checklist

### After Installation
- [ ] App opens without errors
- [ ] Splash screen appears centered
- [ ] Theme matches system (dark/light)
- [ ] Main window centered on screen

### Login
- [ ] Can login to Sandbox
- [ ] Can login to Production
- [ ] Can login with Custom Domain
- [ ] Invalid credentials show error
- [ ] "Show Password" checkbox works

### Backup
- [ ] Can load all objects (no freeze)
- [ ] Can search for objects
- [ ] Can add objects (no duplicates)
- [ ] Can remove objects
- [ ] Progress bar updates 0% → 100%
- [ ] Backup completes successfully
- [ ] #backuplog.txt created
- [ ] CSV files contain data

### Restore
- [ ] Can browse for backup folder
- [ ] Can load backup metadata
- [ ] Progress bar updates during restore
- [ ] #uploadlog.txt created
- [ ] Data imported successfully
- [ ] Checkpoint works if interrupted

### UI
- [ ] No freezing during operations
- [ ] Cancel button works
- [ ] All buttons properly sized
- [ ] No visual gaps or spacing issues
- [ ] Window centered on multiple monitors

---

## 📈 Version History

### v2.0.0 (2025-01-20) - Production Ready Edition
- ✅ Fixed all 17 critical/high/medium priority issues
- ✅ Added comprehensive logging system
- ✅ Implemented auto-reconnect for session timeouts
- ✅ Fixed memory and file handle leaks
- ✅ Added metadata caching (20x faster)
- ✅ Implemented real-time progress bars
- ✅ Fixed window centering on multi-monitor setups
- ✅ Added duplicate selection prevention
- ✅ Moved all magic numbers to settings.py
- ✅ Optimized UI performance (no freezing)

### v1.0.0 (Initial Release)
- ✅ Basic backup and restore functionality
- ✅ Dark/light theme support
- ✅ Splash screen
- ✅ Threading for operations

---

## 🤝 Support

### Getting Help
1. **Check Logs** - Review application and operation logs
2. **Read Docs** - This README covers most issues
3. **Test Isolation** - Try with small dataset first
4. **Restart App** - Clears cache and resets session

### Reporting Issues
Include:
- **Version**: Check `settings.py` for `APP_VERSION`
- **OS**: Windows/macOS/Linux version
- **Operation**: Backup/Restore/Login
- **Logs**: Relevant logs from `~/SFRewind/logs/`
- **Steps**: How to reproduce the issue

---

## 📜 License

Copyright © 2025 SFRewind

---

## 🎉 Acknowledgments

Built with:
- [simple-salesforce](https://github.com/simple-salesforce/simple-salesforce) - Salesforce REST API client
- [tkinter](https://docs.python.org/3/library/tkinter.html) - Python GUI framework
- [pywin32](https://github.com/mhammond/pywin32) - Windows registry access (Windows only)

---

## 🚀 Quick Reference

### Common Commands
```bash
# Start application
python main.py

# Install dependencies
pip install simple-salesforce

# Windows only
pip install pywin32
```

### File Locations
```
~/SFRewind/
├── backups/          # All backup data
├── logs/             # Application logs
└── configs/          # Future: Saved configurations
```

### Default Ports
- None - App doesn't open any ports
- Uses Salesforce REST API over HTTPS

### Default Credentials Location
- Credentials NOT stored
- Re-enter on each session

---

**Ready to backup your Salesforce data? Run `python main.py` and let's get started! 🚀**

For the latest updates, check the `CHANGELOG.md` file.