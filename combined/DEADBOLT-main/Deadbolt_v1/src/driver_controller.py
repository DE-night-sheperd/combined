import os
import sys
import ctypes
import json
from pathlib import Path
import time
import hashlib

try:
    import win32file
    import win32con
    import pywintypes
    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False


class DeadlockDriverController:
    def __init__(self):
        self.driver_name = r"\\.\DeadlockMinifilter"
        self.device_handle = None
        self.auth_required = True
        self.admin_password_hash = None
        self.load_admin_password()

    def load_admin_password(self):
        config_dir = Path.home() / ".deadlock"
        config_dir.mkdir(parents=True, exist_ok=True)
        config_file = config_dir / "admin_config.json"
        
        if config_file.exists():
            try:
                with open(config_file, "r") as f:
                    data = json.load(f)
                    self.admin_password_hash = data.get("admin_password_hash")
            except:
                pass

    def authenticate_admin(self, password):
        if not self.admin_password_hash:
            return password == "DeadlockAdmin2024!"
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        return password_hash == self.admin_password_hash

    def open_driver(self):
        if not HAS_WIN32:
            print("[Driver Controller] pywin32 not available")
            return False

        try:
            self.device_handle = win32file.CreateFile(
                self.driver_name,
                win32con.GENERIC_READ | win32con.GENERIC_WRITE,
                0,
                None,
                win32con.OPEN_EXISTING,
                0,
                None
            )
            print("[Driver Controller] Driver opened successfully")
            return True
        except pywintypes.error as e:
            print(f"[Driver Controller] Failed to open driver: {e}")
            return False

    def close_driver(self):
        if self.device_handle:
            try:
                win32file.CloseHandle(self.device_handle)
                self.device_handle = None
                print("[Driver Controller] Driver closed")
            except:
                pass

    def add_rule(self, path, rule_type, enabled=True):
        if not self.device_handle:
            return False

        IOCTL_DEADLOCK_ADD_RULE = 0x800
        FILE_DEVICE_UNKNOWN = 0x00000022
        METHOD_BUFFERED = 0
        FILE_ANY_ACCESS = 0

        def CTL_CODE(DeviceType, Function, Method, Access):
            return (DeviceType << 16) | (Access << 14) | (Function << 2) | Method

        ioctl_code = CTL_CODE(FILE_DEVICE_UNKNOWN, 0x800, METHOD_BUFFERED, FILE_ANY_ACCESS)

        rule_type_map = {
            "block_all": 0,
            "block_read": 1,
            "block_write": 2,
            "block_delete": 3,
            "block_rename": 4
        }

        try:
            path_bytes = path.encode("utf-16le") + b"\x00\x00"
            
            in_buffer = bytearray(1024)
            offset = 0
            
            in_buffer[offset:offset+2] = (len(path_bytes)).to_bytes(2, byteorder="little")
            offset += 2
            
            in_buffer[offset:offset+2] = (len(path_bytes)).to_bytes(2, byteorder="little")
            offset += 2
            
            ptr_addr = ctypes.addressof(ctypes.c_char.from_buffer(in_buffer, offset))
            in_buffer[offset:offset+8] = ptr_addr.to_bytes(8, byteorder="little")
            offset += 8
            
            rt = rule_type_map.get(rule_type.lower(), 0)
            in_buffer[offset:offset+4] = rt.to_bytes(4, byteorder="little")
            offset += 4
            
            in_buffer[offset:offset+1] = (1 if enabled else 0).to_bytes(1, byteorder="little")
            
            out_buffer = bytearray(1024)
            
            win32file.DeviceIoControl(
                self.device_handle,
                ioctl_code,
                in_buffer,
                out_buffer,
                None
            )
            
            print(f"[Driver Controller] Rule added: {path} ({rule_type})")
            return True
            
        except Exception as e:
            print(f"[Driver Controller] Failed to add rule: {e}")
            return False

    def clear_rules(self):
        if not self.device_handle:
            return False

        try:
            IOCTL_DEADLOCK_CLEAR_RULES = 0x801
            FILE_DEVICE_UNKNOWN = 0x00000022
            METHOD_BUFFERED = 0
            FILE_ANY_ACCESS = 0

            def CTL_CODE(DeviceType, Function, Method, Access):
                return (DeviceType << 16) | (Access << 14) | (Function << 2) | Method

            ioctl_code = CTL_CODE(FILE_DEVICE_UNKNOWN, 0x801, METHOD_BUFFERED, FILE_ANY_ACCESS)
            
            in_buffer = bytearray(0)
            out_buffer = bytearray(1024)
            
            win32file.DeviceIoControl(
                self.device_handle,
                ioctl_code,
                in_buffer,
                out_buffer,
                None
            )
            
            print("[Driver Controller] All rules cleared")
            return True
        except Exception as e:
            print(f"[Driver Controller] Failed to clear rules: {e}")
            return False


if __name__ == "__main__":
    print("=== DEADLOCK DRIVER CONTROLLER ===")
    controller = DeadlockDriverController()
    
    if controller.open_driver():
        print("\nDriver connected!")
        print("\nAvailable commands:")
        print("  add <path> <rule_type> - Add rule (rule_type: block_all, block_read, block_write, block_delete, block_rename)")
        print("  clear - Clear all rules")
        print("  exit - Exit")
        
        while True:
            try:
                cmd = input("\n> ").strip().split()
                if not cmd:
                    continue
                    
                if cmd[0] == "exit":
                    break
                elif cmd[0] == "clear":
                    controller.clear_rules()
                elif cmd[0] == "add" and len(cmd) >= 3:
                    path = cmd[1]
                    rule_type = cmd[2]
                    controller.add_rule(path, rule_type)
                else:
                    print("Unknown command")
            except KeyboardInterrupt:
                break
                
        controller.close_driver()
    else:
        print("\nFailed to connect to driver. Make sure the driver is loaded and running!")
