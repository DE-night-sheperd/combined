import os
import ctypes
from ctypes import wintypes
from pathlib import Path
from typing import Optional

# Windows API definitions
kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
advapi32 = ctypes.WinDLL('advapi32', use_last_error=True)

# Constants
FILE_READ_DATA = 0x0001
FILE_WRITE_DATA = 0x0002
FILE_APPEND_DATA = 0x0004
FILE_READ_EA = 0x0008
FILE_WRITE_EA = 0x0010
FILE_EXECUTE = 0x0020
FILE_DELETE_CHILD = 0x0040
FILE_READ_ATTRIBUTES = 0x0080
FILE_WRITE_ATTRIBUTES = 0x0100
DELETE = 0x00010000
READ_CONTROL = 0x00020000
WRITE_DAC = 0x00040000
WRITE_OWNER = 0x00080000
SYNCHRONIZE = 0x00100000

FILE_ALL_ACCESS = 0x001F01FF
FILE_GENERIC_READ = 0x80000000
FILE_GENERIC_WRITE = 0x40000000
FILE_GENERIC_EXECUTE = 0x20000000

DACL_SECURITY_INFORMATION = 0x00000004
OWNER_SECURITY_INFORMATION = 0x00000001
GROUP_SECURITY_INFORMATION = 0x00000002

class WindowsFilePermissionController:
    def __init__(self):
        self.current_user = os.environ.get('USERNAME', 'Unknown')
        
    def block_access(self, path: str):
        """Set file/folder to read-only and hidden as a basic protection"""
        try:
            path_obj = Path(path)
            if path_obj.exists():
                # Set read-only attribute
                if path_obj.is_file():
                    os.chmod(path, 0o444)
                # Set hidden attribute
                attrs = ctypes.windll.kernel32.GetFileAttributesW(str(path))
                if attrs != -1:
                    ctypes.windll.kernel32.SetFileAttributesW(str(path), attrs | 0x02)
                return True
            return False
        except Exception as e:
            print(f"Error blocking access: {e}")
            return False
            
    def allow_access(self, path: str):
        """Restore normal access to a file/folder"""
        try:
            path_obj = Path(path)
            if path_obj.exists():
                # Restore normal permissions
                os.chmod(path, 0o666)
                # Remove hidden attribute
                attrs = ctypes.windll.kernel32.GetFileAttributesW(str(path))
                if attrs != -1:
                    ctypes.windll.kernel32.SetFileAttributesW(str(path), attrs & ~0x02)
                return True
            return False
        except Exception as e:
            print(f"Error allowing access: {e}")
            return False
            
    def block_write(self, path: str):
        """Block write access to a file/folder"""
        return self.block_access(path)
            
    def block_delete(self, path: str):
        """Block delete access to a file/folder"""
        return self.block_access(path)
