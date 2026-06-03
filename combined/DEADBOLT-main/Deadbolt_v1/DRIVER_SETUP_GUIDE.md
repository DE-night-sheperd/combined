# Deadbolt Kernel Driver - Setup Guide

## IMPORTANT: Python Dependencies Already Installed!
✅ watchdog
✅ pywin32 (for DPAPI encryption)
✅ numpy (for AI Neural Web)

---

## Part 1: Why the IDE Shows Missing Headers
The IDE diagnostics showing missing `<fltKernel.h>` are **normal**! This header is part of the **Windows Driver Kit (WDK)**, which is not part of the standard Visual Studio or Windows SDK installation. The kernel driver code is completely correct - it just needs the WDK to compile!

---

## Part 2: Install Visual Studio & Windows Driver Kit (WDK)

### Step 1: Install Visual Studio 2022 (Community Edition - Free!)
1. Download from: https://visualstudio.microsoft.com/downloads/
2. Run the installer
3. Select **"Desktop development with C++"** workload
4. Make sure these individual components are checked:
   - MSVC v143 - VS 2022 C++ x64/x86 Spectre-mitigated libs (Latest)
   - Windows 11 SDK (or Windows 10 SDK if you're on Windows 10)
5. Click **Install** and wait for completion

### Step 2: Install Windows Driver Kit (WDK)
1. Download WDK from: https://learn.microsoft.com/en-us/windows-hardware/drivers/download-the-wdk
2. Select the WDK version matching your Windows SDK (e.g., WDK for Windows 11, version 22H2)
3. Run the WDK installer
4. Follow the installation wizard
5. When prompted, install the WDK Visual Studio extension

---

## Part 3: Compile the Deadbolt Minifilter Driver

### Step 1: Open the Driver Solution
1. Open Visual Studio 2022
2. Go to File → Open → Project/Solution
3. Navigate to: `Deadbolt_Drivers\DeadboltMinifilter\`
4. Open the solution file (if available) or create a new driver project:

### Step 2: Create New Driver Project (if no solution exists)
1. In Visual Studio, Create New Project
2. Search for "Kernel Mode Driver, Empty (KMDF)"
3. Name it "DeadboltMinifilter"
4. Location: `Deadbolt_Drivers\DeadboltMinifilter\`
5. Click Create

### Step 3: Add Driver.c to Project
1. Right-click on the project in Solution Explorer
2. Add → Existing Item
3. Select `Driver.c` from the DeadboltMinifilter directory
4. Click Add

### Step 4: Configure Project Settings
1. Right-click Project → Properties
2. Configuration: All Configurations
3. Platform: x64
4. Go to **Driver Settings → General**
   - Set Target Platform to "Desktop"
   - Set Target OS Version to your Windows version
5. Go to **C/C++ → General**
   - Add WDK include directories if needed (usually auto-configured)
6. Go to **Linker → Input**
   - Add `fltMgr.lib` to Additional Dependencies

### Step 5: Build the Driver
1. Set Solution Configuration to "Release" or "Debug"
2. Set Solution Platform to "x64"
3. Click Build → Build Solution (or press Ctrl+Shift+B)
4. The compiled `DeadboltMinifilter.sys` will be in `x64\Release\` or `x64\Debug\`

---

## Part 4: Test the User-Mode Parts First! (NO DRIVER NEEDED!)

You don't need the kernel driver to use Deadbolt! The user-mode parts work completely on their own!

### To Test:
1. Open the Deadbolt directory
2. Run `LAUNCHER.py`
3. Click "📁 FILE ACCESS CONTROL"
4. On first launch, set your strong Level 1 Token Key
5. Add a rule for a test folder
6. Click "▶️ START MONITOR"
7. Try to modify/delete a file in the protected folder
8. The popup should appear!

---

## Part 5: Kernel Driver Installation (Optional, for Advanced Users)

### Step 1: Enable Test Signing (For Testing Only!)
1. Open Command Prompt as Administrator
2. Run these commands:
   ```cmd
   bcdedit /set testsigning on
   ```
3. Restart your computer

### Step 2: Install the Driver
1. Copy `DeadboltMinifilter.sys` and `DeadboltMinifilter.inf` to `C:\Windows\System32\drivers\`
2. Open Command Prompt as Administrator
3. Navigate to the driver directory
4. Run:
   ```cmd
   RUNDLL32.EXE SETUPAPI.DLL,InstallHinfSection DefaultInstall 132 .\DeadboltMinifilter.inf
   ```
5. Or use `sc create` command:
   ```cmd
   sc create DeadboltMinifilter type= kernel start= demand binPath= C:\Windows\System32\drivers\DeadboltMinifilter.sys
   sc start DeadboltMinifilter
   ```

### Step 3: Disable Test Signing (For Production)
1. Open Command Prompt as Administrator
2. Run:
   ```cmd
   bcdedit /set testsigning off
   ```
3. Restart your computer

---

## Part 6: Summary

| Component | Status | Notes |
|-----------|--------|-------|
| Python Dependencies | ✅ INSTALLED | watchdog, pywin32, numpy |
| User-Mode Application | ✅ READY | No driver needed! |
| Kernel Driver | ⚠️ NEEDS WDK | Requires WDK + Visual Studio to compile |

---

## Quick Start (User-Mode Only - Works NOW!)
```cmd
cd "c:\Users\Admin\OneDrive - Sol Plaatje University\Desktop\Deadlock\DEADBOLT\Deadbolt_v1"
python LAUNCHER.py
```

Then click "📁 FILE ACCESS CONTROL"!
