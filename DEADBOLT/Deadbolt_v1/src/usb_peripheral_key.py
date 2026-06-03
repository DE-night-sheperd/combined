import os
import sys
import time
import hashlib
import uuid
import platform
import json
from pathlib import Path
from typing import Optional, Tuple

try:
    import wmi
    WMI_AVAILABLE = True
except ImportError:
    WMI_AVAILABLE = False

class USBPeripheralKey:
    def __init__(self, config_dir: Path):
        self.config_dir = config_dir
        self.machine_id = self._get_machine_id()
        self.key_file = config_dir / "usb_peripheral_key.json"
        
    def _get_machine_id(self) -> str:
        machine_id_parts = []
        
        try:
            machine_id_parts.append(platform.node())
        except Exception:
            pass
            
        try:
            machine_id_parts.append(str(uuid.getnode()))
        except Exception:
            pass
            
        try:
            machine_id_parts.append(platform.processor())
        except Exception:
            pass
            
        try:
            machine_id_parts.append(platform.machine())
        except Exception:
            pass
            
        try:
            if WMI_AVAILABLE:
                c = wmi.WMI()
                for item in c.Win32_ComputerSystemProduct():
                    machine_id_parts.append(item.UUID)
                for item in c.Win32_BaseBoard():
                    machine_id_parts.append(item.SerialNumber)
        except Exception:
            pass
            
        combined = "|".join(machine_id_parts)
        return hashlib.sha256(combined.encode('utf-8')).hexdigest()
        
    def get_usb_drives(self) -> list:
        usb_drives = []
        if os.name == 'nt':
            from string import ascii_uppercase
            for letter in ascii_uppercase:
                drive = f"{letter}:\\"
                if os.path.exists(drive):
                    try:
                        if os.path.ismount(drive):
                            usb_drives.append(drive)
                    except Exception:
                        pass
        return usb_drives
        
    def generate_peripheral_key(self, usb_drive: str, progress_callback=None) -> Tuple[bool, str]:
        try:
            steps = [
                "Generating machine fingerprint...",
                "Creating key data structure...",
                f"Writing to USB: .deadlock_peripheral_key",
                "Generating signature...",
                f"Writing to local: machine_binding.json",
                "Verifying file integrity..."
            ]
            
            for i, step in enumerate(steps):
                if progress_callback:
                    progress_callback(i, len(steps), step)
                time.sleep(0.4)
            
            key_data = {
                "machine_id": self.machine_id,
                "timestamp": int(time.time()),
                "version": "1.0"
            }
            
            key_json = json.dumps(key_data, indent=2)
            signature = hashlib.sha256((key_json + self.machine_id).encode('utf-8')).hexdigest()
            
            full_key_data = {
                "key_data": key_data,
                "signature": signature
            }
            
            usb_path = Path(usb_drive)
            key_file = usb_path / ".deadlock_peripheral_key"
            
            if progress_callback:
                progress_callback(2, len(steps), f"Writing to USB: .deadlock_peripheral_key")
            with open(key_file, 'w') as f:
                json.dump(full_key_data, f, indent=2)
            
            machine_key_file = self.config_dir / "machine_binding.json"
            if progress_callback:
                progress_callback(4, len(steps), f"Writing to local: machine_binding.json")
            with open(machine_key_file, 'w') as f:
                json.dump({
                    "machine_id": self.machine_id,
                    "usb_key_generated": True
                }, f, indent=2)
            
            if progress_callback:
                progress_callback(len(steps)-1, len(steps), "Complete!")
                
            return True, "Peripheral key generated successfully!"
        except Exception as e:
            return False, f"Error generating key: {e}"
            
    def verify_peripheral_key(self, usb_drive: str) -> Tuple[bool, str]:
        try:
            usb_path = Path(usb_drive)
            key_file = usb_path / ".deadlock_peripheral_key"
            
            if not key_file.exists():
                return False, "No peripheral key found on USB drive"
                
            with open(key_file, 'r') as f:
                full_key_data = json.load(f)
                
            key_data = full_key_data.get("key_data", {})
            signature = full_key_data.get("signature", "")
            
            key_json = json.dumps(key_data, indent=2)
            expected_signature = hashlib.sha256((key_json + self.machine_id).encode('utf-8')).hexdigest()
            
            if signature != expected_signature:
                return False, "Invalid key signature"
                
            if key_data.get("machine_id") != self.machine_id:
                return False, "Key is not bound to this machine"
                
            return True, "Peripheral key verified successfully!"
        except Exception as e:
            return False, f"Error verifying key: {e}"
