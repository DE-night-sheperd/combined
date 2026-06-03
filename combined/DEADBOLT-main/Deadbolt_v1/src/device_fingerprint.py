import os
import platform
import uuid
import socket
import json
from typing import Dict, Any

try:
    import wmi
    WMI_AVAILABLE = True
except ImportError:
    WMI_AVAILABLE = False

def get_device_fingerprint() -> Dict[str, Any]:
    fingerprint = {}
    
    # Basic system info
    fingerprint["hostname"] = socket.gethostname()
    fingerprint["os"] = platform.system()
    fingerprint["os_version"] = platform.version()
    fingerprint["os_release"] = platform.release()
    fingerprint["machine"] = platform.machine()
    fingerprint["processor"] = platform.processor()
    
    # Network info
    try:
        hostname, aliases, ip_addresses = socket.gethostbyname_ex(socket.gethostname())
        fingerprint["ip_addresses"] = ip_addresses
    except Exception:
        fingerprint["ip_addresses"] = ["unavailable"]
    
    # MAC address
    try:
        mac = uuid.getnode()
        fingerprint["mac_address"] = ':'.join(('%012X' % mac)[i:i+2] for i in range(0, 12, 2))
    except Exception:
        fingerprint["mac_address"] = "unavailable"
    
    # WMI info (Windows only)
    if WMI_AVAILABLE and platform.system() == "Windows":
        try:
            c = wmi.WMI()
            
            # Motherboard info
            for board in c.Win32_BaseBoard():
                fingerprint["motherboard_serial"] = board.SerialNumber if board.SerialNumber else "n/a"
                fingerprint["motherboard_product"] = board.Product if board.Product else "n/a"
            
            # BIOS info
            for bios in c.Win32_BIOS():
                fingerprint["bios_serial"] = bios.SerialNumber if bios.SerialNumber else "n/a"
                fingerprint["bios_version"] = bios.Version if bios.Version else "n/a"
            
            # CPU info
            for cpu in c.Win32_Processor():
                fingerprint["cpu_id"] = cpu.ProcessorId if cpu.ProcessorId else "n/a"
                fingerprint["cpu_name"] = cpu.Name if cpu.Name else "n/a"
            
            # Disk drives
            disks = []
            for disk in c.Win32_DiskDrive():
                disks.append({
                    "model": disk.Model if disk.Model else "n/a",
                    "serial": disk.SerialNumber if disk.SerialNumber else "n/a"
                })
            fingerprint["disk_drives"] = disks
            
        except Exception as e:
            fingerprint["wmi_error"] = str(e)
    
    # Username
    try:
        fingerprint["username"] = os.getenv("USERNAME", os.getenv("USER", "unknown"))
    except Exception:
        fingerprint["username"] = "unknown"
    
    return fingerprint

def get_fingerprint_json() -> str:
    return json.dumps(get_device_fingerprint(), indent=2)
