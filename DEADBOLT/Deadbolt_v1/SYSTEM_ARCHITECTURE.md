# DEADLOCK ENDPOINT SHIELD - SYSTEM ARCHITECTURE v1.0

## High‑Level Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                          USER INTERFACE LAYER                        │
├─────────────────────────────────────────────────────────────────────┤
│  LAUNCHER.py → Pixel Lock Animation → Professional Wizard →        │
│  Key Gen Wizard → retro_ui.py (or other interfaces)                │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│                      CORE SECURITY MODULES LAYER                    │
├─────────────────────────────────────────────────────────────────────┤
│  ┌──────────────────┐  ┌──────────────────┐  ┌─────────────────┐ │
│  │  Admin Security  │  │ Threat Detection │  │ Token Auth     │ │
│  │  (Audit Logging, │  │  (Ransomware,    │  │ (USB Key)      │ │
│  │   Device FP)     │  │   Mass Ops)      │  └─────────────────┘ │
│  └──────────────────┘  └──────────────────┘  ┌─────────────────┐ │
│  ┌──────────────────┐  ┌──────────────────┐  │ File Access     │ │
│  │ Security Utils   │  │ File Monitor     │  │ Control         │ │
│  │ (Hashing, DPAPI) │  │ (Watchdog)       │  └─────────────────┘ │
│  └──────────────────┘  └──────────────────┘  ┌─────────────────┐ │
│                                              │ Security Sandbox │ │
│                                              └─────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│                      DATA STORAGE LAYER                              │
├─────────────────────────────────────────────────────────────────────┤
│  %USERPROFILE%\.deadlock\                                            │
│    ├── admin_config.json          (admin credentials hash)         │
│    ├── admin_audit.log            (admin activity log)             │
│    ├── token_config.json          (encrypted token)                 │
│    ├── .hmac_key                  (HMAC key)                       │
│    └── .first_launch              (first‑launch flag)              │
│                                                                      │
│  %PROGRAMDATA%\DeadlockEndpointShield\                              │
│    └── config.json                (professional install config)     │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│                      KERNEL‑MODE LAYER (DRIVER)                     │
├─────────────────────────────────────────────────────────────────────┤
│  DeadboltMinifilter.sys                                              │
│  (File system minifilter for low‑level file access monitoring)     │
└─────────────────────────────────────────────────────────────────────┘
```

## Module Descriptions

### 1. Entry Point (LAUNCHER.py)
- **Responsibility**: Orchestrates full application startup flow
- **Flow**:
  1. Pixel Lock logo animation
  2. Professional Setup Wizard (if not installed)
  3. Key Generation Wizard (if first launch)
  4. Main Application UI

### 2. Core Security Modules

#### Admin Security (src/retro_ui.py: AdminAuthenticator)
- SHA‑256 password hashing (never stores plain text)
- Audit logging (timestamps + device fingerprints)
- Device fingerprinting (hostname, OS, MAC, IP, motherboard, BIOS, CPU, disks)
- Password complexity enforcement

#### Threat Detection (src/threat_detector.py)
- Ransomware extension detection (locky, zepto, wannacry, etc.)
- Mass file operation detection (modifications/creations/renames per second)
- Real‑time event analysis

#### Token Authentication (src/file_operation_monitor.py: TokenAuthenticator)
- USB peripheral key support
- DPAPI‑encrypted token storage
- HMAC signing for verification

#### File Operation Monitor (src/file_operation_monitor.py)
- Uses `watchdog` library for real‑time file system monitoring
- Integrates with ThreatDetector
- Blocks unauthorized operations
- Requires token for allow/deny decisions

#### Security Utilities (src/security_utils.py)
- Secure config directory handling
- HMAC key generation
- DPAPI encryption/decryption (Windows only)
- Password complexity validation

### 3. UI Interfaces
- retro_ui.py (main retro‑style admin UI)
- security_sandbox.py
- control_center.py
- file_access_control.py
- usb_peripheral_key.py

### 4. Installation Wizards
- DEADLOCK_PROFESSIONAL_WIZARD.py (Windows‑style installer)
- DEADLOCK_INSTALL_WIZARD.py (key generation)

## Security Design Principles
1. **Defense in Depth**: Multiple layers (UI → Core → Kernel)
2. **Least Privilege**: Admin actions require explicit authentication
3. **Secure Storage**: Sensitive data encrypted/hashed, never plain text
4. **Audit Everything**: All admin actions logged with device fingerprints
5. **Threat‑Oriented**: Ransomware and mass‑operation detection built‑in
