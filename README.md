# SFRewind - Salesforce Sandbox Backup & Restore

## 🆕 Latest Updates

### ✅ New Features

1. **🎨 Automatic System Theme Detection**
   - Detects Windows/macOS/Linux dark mode
   - Automatically applies dark/light theme
   - No manual toggle needed - respects system preferences

2. **🚀 Splash Screen on Startup**
   - Professional loading screen with SFRewind branding
   - Shows loading progress
   - Centered on screen from start (no glitching)

3. **⚡ Full Threading Implementation**
   - All Salesforce operations run in background threads
   - **No UI freezing** during:
     - Login/Connection
     - Loading all objects
     - Searching objects
     - Adding objects (field detection)
     - Backup process
     - Restore process
   - UI remains responsive at all times

4. **🎯 Fixed Window Centering**
   - Window opens directly in center
   - No position jumping/glitching

## 📁 Updated Project Structure

```
SFRewind/
├── main.py                     # Entry point with splash screen
├── requirements.txt            # Dependencies
├── config/
│   ├── __init__.py
│   └── settings.py            # Settings
├── core/                       # Business logic
│   ├── __init__.py
│   ├── salesforce_auth.py     # Authentication (dynamic API)
│   ├── backup_manager.py      # Backup with logging
│   └── restore_manager.py     # Restore with logging
├── ui/                         # User interface
│   ├── __init__.py
│   ├── main_window.py         # Main window (theme-aware)
│   ├── login_frame.py         # Login (custom domain support)
│   ├── backup_frame.py        # Backup (fully threaded)
│   └── restore_frame.py       # Restore (fully threaded)
└── utils/                      # NEW - Utilities
    ├── __init__.py
    ├── splash_screen.py       # Splash screen
    └── theme_manager.py       # Theme detection & application
```

## 🎨 Theme Detection

### How It Works

**Windows:**
- Reads registry: `HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize`
- Checks `AppsUseLightTheme` value (0 = Dark, 1 = Light)

**macOS:**
- Runs: `defaults read -g AppleInterfaceStyle`
- Checks for "Dark" in output

**Linux:**
- Runs: `gsettings get org.gnome.desktop.interface gtk-theme`
- Checks for "dark" in theme name

### Color Schemes

**Dark Mode:**
- Background: `#1E1E1E`
- Text: `#E0E0E0`
- Accent: `#00A1E0` (Salesforce Blue)
- Entry fields: `#2D2D2D`

**Light Mode:**
- Background: `#FFFFFF`
- Text: `#000000`
- Accent: `#00A1E0` (Salesforce Blue)
- Entry fields: `#FFFFFF`

## 🚀 Installation

### 1. Install Dependencies

```bash
pip install simple-salesforce
```

**Windows Users - Additional Requirement:**
```bash
pip install pywin32
```
This is needed for Windows registry access (dark mode detection).

### 2. Create New Folder

Add the new `utils/` folder to your project:

```bash
mkdir utils
```

### 3. Copy Files

Copy these **NEW** files:
- `utils/__init__.py`
- `utils/splash_screen.py`
- `utils/theme_manager.py`

Replace these **UPDATED** files:
- `main.py`
- `core/salesforce_auth.py`
- `ui/main_window.py`
- `ui/login_frame.py`
- `ui/backup_frame.py`
- `ui/restore_frame.py`

## 🎯 Running the Application

```bash
python main.py
```

### What Happens:

1. **Splash Screen** appears (centered, no glitch)
2. **System theme** detected automatically
3. **Components** loaded in background
4. **Theme applied** to all UI elements
5. **Main window** appears (already centered)
6. **Ready to use!**

## ⚡ Threading Details

### All Threaded Operations:

| Operation | UI Status | Details |
|-----------|-----------|---------|
| **Login** | Responsive | Connection in background |
| **Load All Objects** | Responsive | Queries org in background |
| **Search Objects** | Responsive | Searches in background if needed |
| **Add Object** | Responsive | Field detection in background |
| **Backup** | Responsive | Export runs in background |
| **Restore** | Responsive | Import runs in background |

### Progress Indicators:

- All operations show progress messages
- Progress bars animate during operations
- Status updates in real-time
- UI never freezes

## 🎨 Theme Examples

### Dark Mode
```
Background: Dark gray (#1E1E1E)
Text: Light gray (#E0E0E0)
Input fields: Darker gray (#2D2D2D)
Buttons: Salesforce Blue (#00A1E0)
```

### Light Mode
```
Background: White (#FFFFFF)
Text: Black (#000000)
Input fields: White (#FFFFFF)
Buttons: Salesforce Blue (#00A1E0)
```

## 🐛 Troubleshooting

### Splash Screen Not Showing
- Check if `utils/` folder exists
- Ensure `utils/__init__.py` is present

### Theme Not Detected
- **Windows**: Run as user (not admin) for registry access
- **macOS**: System Preferences → General → Appearance
- **Linux**: Check GNOME settings if using GNOME

### UI Still Freezing
- Check if operation is actually threaded
- Look for `threading.Thread(target=..., daemon=True).start()`
- Verify no blocking operations in main thread

### Import Errors
```bash
# If you see: ModuleNotFoundError: No module named 'utils'
# Make sure utils/__init__.py exists
touch utils/__init__.py
```

## 📝 Notes

### Theme Updates
- Theme is detected **once** at startup
- To refresh theme: Restart application
- System theme changes require app restart

### Performance
- First "Load All Objects" takes 2-5 seconds (300+ objects)
- Subsequent searches are instant (cached)
- Adding objects: 1-2 seconds per object
- Backup/Restore: Depends on data volume

### Splash Screen Timing
- Default: ~2 seconds total
- Adjust in `main.py` by changing `time.sleep()` values
- Minimum recommended: 1.5 seconds (for smooth experience)

## 🎯 Best Practices

1. **Let operations complete**: Don't close app during backup/restore
2. **Check logs**: Review `#backuplog.txt` and `#uploadlog.txt`
3. **Test first**: Use small datasets for testing
4. **Monitor progress**: Watch status messages and progress bars

## 🔥 Features Summary

✅ Automatic dark/light theme
✅ Professional splash screen  
✅ No UI freezing (full threading)
✅ Centered window (no glitch)
✅ Dynamic API detection
✅ Custom domain support
✅ Detailed logging
✅ Record count display
✅ Logout from anywhere

Enjoy SFRewind! 🚀