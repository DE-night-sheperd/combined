# DEADLOCK ENDPOINT SHIELD v1.0

A professional, multi-layered endpoint security system for Windows.

## Features

### Core Security
- **AI-Powered Threat Detection** (Random Forest classifier with rule-based backup)
- **Real‑time File Operation Monitoring**
- **Ransomware Detection & Mitigation**
- **Zip Bomb Protection**
- **USB Peripheral Key Authentication**
- **Security Sandbox with AI Analysis**
- **Admin Authentication & Audit Logging**
- **Device Fingerprinting**
- **User Management (Allowed Users List)**
- **Comprehensive Security Monitor**:
  - Remote access detection
  - Multiple user detection
  - Wi-Fi/hotspot/mic/camera disable on threats
  - System lock after 3 failed attempts + USB token unlock
  - Unauthorized user detection

### Installation Flow
1. **Pixel Lock Logo Animation** - Branded intro sequence
2. **Professional Setup Wizard** - Full Windows‑style installer
3. **Key Generation Wizard** - USB‑based token setup (with skip option)
4. **Main Application** - Choose your interface

## Installation

### System Requirements
- Windows 10 or 11
- Python 3.10+
- Administrator privileges (for driver installation)
- Python Packages: scikit-learn, numpy, pywin32, wmi

### Quick Start
1. Run `LAUNCHER.py`
2. Follow the setup wizard
3. Complete key generation (or skip for limited functionality)
4. Enjoy Deadlock Endpoint Shield!

## Admin Guide

### Default Credentials
- Username: `admin`
- Password: `DeadlockAdmin2024!`

**IMPORTANT: Change the default password immediately on first login!**

### Admin Features
1. **Audit Log**: View all admin actions with timestamps and device fingerprints
2. **Change Password**: Enforces strong password complexity
3. **Device Fingerprinting**: Every login attempt includes full device details
4. **Manage Allowed Users**: Add/remove users to control who can access the system
5. **USB Token Warning**: Auto-warning on login if no peripheral token detected

### Audit Log Location
```
%USERPROFILE%\.deadlock\admin_audit.log
```

## Developers

### System Architecture
See [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md) for a complete high‑level system architecture diagram and module descriptions.

### Project Structure
```
Deadbolt_v1/
├── LAUNCHER.py                      # Main entry point
├── DEADLOCK_PROFESSIONAL_WIZARD.py  # Professional installer
├── DEADLOCK_INSTALL_WIZARD.py      # Key generation wizard
├── driver_installer.py              # Driver installation script
├── SYSTEM_ARCHITECTURE.md           # System architecture document
├── Deadlock_Documentation.tex       # Full LaTeX documentation
├── README.md                         # This file
├── src/
│   ├── retro_ui.py                  # Main retro‑style UI
│   ├── device_fingerprint.py        # Device fingerprinting module
│   ├── threat_detector.py           # Threat detection (ransomware, mass ops)
│   ├── ai_threat_detector.py        # AI-powered threat detection (Random Forest)
│   ├── security_utils.py            # Security utilities
│   ├── file_operation_monitor.py
│   ├── security_sandbox.py          # Security sandbox with AI integration
│   ├── control_center.py
│   ├── file_access_control.py
│   ├── usb_peripheral_key.py
│   ├── driver_controller.py          # Driver control (add/clear rules)
│   └── security_monitor.py          # Comprehensive security monitor
├── tests/
│   └── test_security.py             # Security unit tests
└── Deadbolt_Drivers/                # Minifilter driver
    ├── DeadboltMinifilter/
    ├── DeadboltMonitor/
    └── DeadboltMonitor_Extended/
```

### Running Tests
```bash
cd Deadbolt_v1
python tests\test_security.py
```

## License
Copyright © 2026 INDEX[0] (Deadlock Endpoint Shield). All rights reserved.

## Trademark Notice
Deadlock® and the Pixel Lock logo are trademarks of INDEX[0].
