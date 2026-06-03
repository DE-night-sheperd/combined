import ctypes
import os
import sys
from ctypes import wintypes

kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)

DEVICE_NAME = r"\\.\DeadboltMinifilter"
GENERIC_READ = 0x80000000
GENERIC_WRITE = 0x40000000
OPEN_EXISTING = 3
FILE_ATTRIBUTE_NORMAL = 0x80

FILE_DEVICE_UNKNOWN = 0x00000022
METHOD_BUFFERED = 0
FILE_ANY_ACCESS = 0

def CTL_CODE(DeviceType, Function, Method, Access):
    return (DeviceType << 16) | (Access << 14) | (Function << 2) | Method

IOCTL_DEADBOLT_ADD_RULE = CTL_CODE(FILE_DEVICE_UNKNOWN, 0x800, METHOD_BUFFERED, FILE_ANY_ACCESS)
IOCTL_DEADBOLT_CLEAR_RULES = CTL_CODE(FILE_DEVICE_UNKNOWN, 0x801, METHOD_BUFFERED, FILE_ANY_ACCESS)

class UNICODE_STRING(ctypes.Structure):
    _fields_ = [
        ("Length", wintypes.USHORT),
        ("MaximumLength", wintypes.USHORT),
        ("Buffer", ctypes.POINTER(wintypes.WCHAR))
    ]

class DEADBOLT_ACCESS_RULE(ctypes.Structure):
    _fields_ = [
        ("Path", UNICODE_STRING),
        ("RuleType", ctypes.c_uint),
        ("Enabled", wintypes.BOOLEAN)
    ]

class DriverConnector:
    def __init__(self):
        self.device_handle = None
        
    def connect(self):
        self.device_handle = kernel32.CreateFileW(
            DEVICE_NAME,
            GENERIC_READ | GENERIC_WRITE,
            0,
            None,
            OPEN_EXISTING,
            FILE_ATTRIBUTE_NORMAL,
            None
        )
        if self.device_handle == wintypes.HANDLE(-1).value:
            raise ctypes.WinError(ctypes.get_last_error())
        return True
    
    def disconnect(self):
        if self.device_handle is not None:
            kernel32.CloseHandle(self.device_handle)
            self.device_handle = None
    
    def clear_rules(self):
        if self.device_handle is None:
            raise Exception("Not connected to driver")
            
        bytes_returned = wintypes.DWORD()
        result = kernel32.DeviceIoControl(
            self.device_handle,
            IOCTL_DEADBOLT_CLEAR_RULES,
            None,
            0,
            None,
            0,
            ctypes.byref(bytes_returned),
            None
        )
        if not result:
            raise ctypes.WinError(ctypes.get_last_error())
        return True
    
    def add_rule(self, path: str, rule_type: int, enabled: bool = True):
        if self.device_handle is None:
            raise Exception("Not connected to driver")
            
        path_wide = ctypes.create_unicode_buffer(path)
        unicode_str = UNICODE_STRING(
            Length=len(path) * 2,
            MaximumLength=(len(path) + 1) * 2,
            Buffer=ctypes.cast(path_wide, ctypes.POINTER(wintypes.WCHAR))
        )
        
        rule = DEADBOLT_ACCESS_RULE(
            Path=unicode_str,
            RuleType=rule_type,
            Enabled=enabled
        )
        
        bytes_returned = wintypes.DWORD()
        result = kernel32.DeviceIoControl(
            self.device_handle,
            IOCTL_DEADBOLT_ADD_RULE,
            ctypes.byref(rule),
            ctypes.sizeof(rule),
            None,
            0,
            ctypes.byref(bytes_returned),
            None
        )
        if not result:
            raise ctypes.WinError(ctypes.get_last_error())
        return True
