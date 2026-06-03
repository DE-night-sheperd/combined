# DEADBOLT ENDPOINT SHIELD - CUSTOM WINDOWS DRIVERS

## Overview
This folder contains **real Windows kernel-mode drivers** for Deadbolt Endpoint Shield, built with the Windows Driver Kit (WDK) and Kernel-Mode Driver Framework (KMDF).

---

## Components
1. **DeadboltMonitor.sys** - Kernel-mode driver for low-level system monitoring
2. **DeadboltController.exe** - User-mode app to communicate with the driver

---

## Prerequisites
To build and test these drivers:
1. Windows 10/11 SDK
2. Windows Driver Kit (WDK) 10/11
3. Visual Studio 2022 with "Desktop development with C++" and "Driver development" workloads
4. A **Virtual Machine (VM)** for testing (NEVER test kernel-mode drivers on your host OS!)

---

## Test Signing (Critical!)
Windows requires drivers to be signed. For testing:
```cmd
# Enable test signing on the test VM
bcdedit /set testsigning on
# Reboot the VM
```

---

## Build Instructions
1. Open `Deadbolt_Drivers.sln` in Visual Studio 2022
2. Select **x64** and **Debug** or **Release**
3. Build the solution (F7)

---

## Loading the Driver (Test VM Only!)
```cmd
# Create driver service
sc create DeadboltMonitor type= kernel binPath= C:\Path\To\DeadboltMonitor.sys

# Start the driver
sc start DeadboltMonitor

# Check driver status
sc query DeadboltMonitor

# Stop the driver
sc stop DeadboltMonitor

# Delete the driver service
sc delete DeadboltMonitor
```

---

## Safety Notes
- ALWAYS test drivers in a Virtual Machine (VM)
- NEVER run unsigned/untrusted drivers on your host OS
- Keep snapshots of your VM so you can roll back if needed
- Kernel-mode drivers can cause blue screens (BSOD) if buggy - this is normal during development!

---

## More Info
- Microsoft WDK Documentation: https://learn.microsoft.com/en-us/windows-hardware/drivers/
- KMDF Documentation: https://learn.microsoft.com/en-us/windows-hardware/drivers/wdf/
