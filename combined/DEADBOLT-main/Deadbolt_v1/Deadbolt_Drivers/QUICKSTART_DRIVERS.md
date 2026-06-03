# 🚀 DEADBOLT DRIVERS - QUICKSTART GUIDE

---

## ✅ What We've Built

### 1. **DeadboltMonitor.sys** (Kernel-Mode Driver)
- Built with KMDF (Kernel-Mode Driver Framework) - modern, safe, Microsoft-recommended
- Features:
  - Start/Stop monitoring via IOCTL commands
  - Get driver status
  - Ready to be extended with file system minifilters, process callbacks, network monitoring, etc.

### 2. **DeadboltController.exe** (User-Mode App)
- Communicates with the kernel driver via IOCTL
- Commands: `start`, `stop`, `status`

---

## 📂 Deadbolt_Drivers/ Folder Structure
```
Deadbolt_Drivers/
├── README.md                   ← Full documentation
├── QUICKSTART_DRIVERS.md       ← This file!
├── DeadboltMonitor/
│   ├── Driver.c                ← ✅ Kernel driver source
│   └── DeadboltMonitor.inf     ← ✅ Driver INF file
└── DeadboltController/
    └── Controller.cpp          ← ✅ User-mode controller source
```

---

## 🔧 Next Steps to Extend the Driver

### For a Real EDR, Add These Capabilities to the Driver:

1. **File System Minifilter** (Monitor file reads/writes/deletes)
   - Use `FltRegisterFilter()`
   - Catch `IRP_MJ_READ`, `IRP_MJ_WRITE`, `IRP_MJ_SET_INFORMATION`, etc.

2. **Process Creation Callbacks**
   - Use `PsSetCreateProcessNotifyRoutineEx()`
   - Monitor every new process

3. **Thread Creation Callbacks**
   - Use `PsSetCreateThreadNotifyRoutine()`
   - Monitor every new thread

4. **Image Load Callbacks**
   - Use `PsSetLoadImageNotifyRoutine()`
   - Monitor every DLL/EXE loaded

5. **Registry Callbacks**
   - Use `CmRegisterCallbackEx()`
   - Monitor registry changes

6. **Network Monitoring**
   - Use WFP (Windows Filtering Platform)
   - Monitor incoming/outgoing network traffic

---

## 📚 Resources to Learn More

- **Microsoft WDK Documentation**: https://learn.microsoft.com/en-us/windows-hardware/drivers/
- **KMDF Documentation**: https://learn.microsoft.com/en-us/windows-hardware/drivers/wdf/
- **Windows Driver Samples**: https://github.com/microsoft/Windows-driver-samples
- **File System Minifilter Samples**: Look for "minifilter" in the Windows-driver-samples repo
- **WFP (Windows Filtering Platform)**: https://learn.microsoft.com/en-us/windows/win32/fwp/windows-filtering-platform-start-page

---

## ⚠️ CRITICAL SAFETY REMINDERS

- **NEVER TEST KERNEL-MODE DRIVERS ON YOUR HOST OS!**
- **ALWAYS USE A VIRTUAL MACHINE (VM)!**
- **ENABLE TEST SIGNING ON THE VM ONLY!**
- **KEEP VM SNAPSHOTS!** Roll back if you get a BSOD!
- Kernel-mode drivers run with **full system privileges** - a single bug can crash the entire OS!

---

## 🎯 Summary

You now have:
1. ✅ A working KMDF kernel-mode driver skeleton
2. ✅ A user-mode app to communicate with it
3. ✅ Complete documentation
4. ✅ A roadmap to extend it into a real EDR driver!

**Your Deadbolt Endpoint Shield now has custom Windows kernel-mode drivers! 🚀**
