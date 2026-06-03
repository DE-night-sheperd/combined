# Deadbolt File Access Control - Setup Guide

## Overview
The Deadbolt File Access Control system consists of two parts:
1. **User-Mode Controller** (Python) - Rules management and UI
2. **Kernel-Mode Minifilter Driver** (C) - System-level enforcement

---

## Part 1: User-Mode Setup (No Driver Required)
The user-mode controller works immediately and provides:
- Rule management UI
- Persistent rule storage
- User-mode access checking

### To use:
1. Run `LAUNCHER.py`
2. Click "📁 FILE ACCESS CONTROL"
3. Add rules to protect your files/folders!

---

## Part 2: Kernel-Mode Driver Setup (Optional, For Full System Enforcement)
### Requirements:
- Windows 10/11
- Windows Driver Kit (WDK) 10+
- Visual Studio 2022 with C++ and Driver development components

### Compilation Steps:
1. Open Visual Studio
2. Create a new "Kernel Mode Driver, Empty (KMDF)" project
3. Add `Deadbolt_Drivers/DeadboltMinifilter/Driver.c` to the project
4. Add `Deadbolt_Drivers/DeadboltMinifilter/DeadboltMinifilter.inf` to the project
5. Configure project settings for minifilter:
   - Target Platform: Windows 10+
   - Configuration: Release
   - Platform: x64
6. Build the solution
7. The compiled `DeadboltMinifilter.sys` will be in the output directory

### Installation Steps:
1. Open Command Prompt as Administrator
2. Navigate to the driver directory
3. Run: `sc create DeadboltMinifilter type= kernel start= demand binPath= "C:\Path\To\DeadboltMinifilter.sys"`
4. Run: `sc start DeadboltMinifilter`
5. Or use the INF file to install via Device Manager

---

## File Structure:
```
Deadbolt_v1/
├── LAUNCHER.py                      # Main launcher
├── FILE_ACCESS_MANAGER.py           # File access UI
├── TEST_FILE_ACCESS.py             # Test script
├── FILE_ACCESS_SETUP_GUIDE.md       # This file
├── src/
│   ├── file_access_control.py       # Core access controller
│   ├── driver_connector.py         # Driver communication
│   └── file_access_service.py       # Background service
└── Deadbolt_Drivers/
    └── DeadboltMinifilter/
        ├── Driver.c                 # Minifilter driver
        └── DeadboltMinifilter.inf   # Driver INF
```
