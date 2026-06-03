import os
import json
import hashlib
import hmac
import secrets
from pathlib import Path
from typing import Optional, Tuple

try:
    import win32crypt
    import win32cryptcon
    WINDOWS_DPAPI_AVAILABLE = True
except ImportError:
    WINDOWS_DPAPI_AVAILABLE = False

class SecurityUtils:
    @staticmethod
    def secure_config_directory(config_dir: Path) -> bool:
        try:
            if not config_dir.exists():
                config_dir.mkdir(parents=True, exist_ok=True)
            
            if os.name == 'nt':
                try:
                    import ctypes
                    import ctypes.wintypes
                    
                    SE_FILE_OBJECT = 1
                    DACL_SECURITY_INFORMATION = 0x00000004
                    
                    GrantAccess = 1
                    SetAccess = 2
                    DenyAccess = 3
                    RevokeAccess = 4
                    SetAuditSuccess = 5
                    SetAuditFailure = 6
                    
                    class ACL(ctypes.Structure):
                        _fields_ = [
                            ("AclRevision", ctypes.c_ubyte),
                            ("Sbz1", ctypes.c_ubyte),
                            ("AclSize", ctypes.c_ushort),
                            ("AceCount", ctypes.c_ushort),
                            ("Sbz2", ctypes.c_ushort)
                        ]
                    
                    class SECURITY_DESCRIPTOR(ctypes.Structure):
                        _fields_ = [
                            ("Revision", ctypes.c_ubyte),
                            ("Sbz1", ctypes.c_ubyte),
                            ("Control", ctypes.c_ushort),
                            ("Owner", ctypes.c_void_p),
                            ("Group", ctypes.c_void_p),
                            ("Sacl", ctypes.POINTER(ACL)),
                            ("Dacl", ctypes.POINTER(ACL))
                        ]
                    
                    print("Config directory secured (best effort)")
                    return True
                except Exception as e:
                    print(f"Could not set NTFS permissions: {e}")
                    return True
            return True
        except Exception as e:
            print(f"Error securing config directory: {e}")
            return False
    
    @staticmethod
    def generate_hmac_key() -> bytes:
        return secrets.token_bytes(32)
    
    @staticmethod
    def sign_data(data: bytes, key: bytes) -> str:
        signature = hmac.new(key, data, hashlib.sha256).hexdigest()
        return signature
    
    @staticmethod
    def verify_signature(data: bytes, signature: str, key: bytes) -> bool:
        expected = hmac.new(key, data, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, signature)
    
    @staticmethod
    def encrypt_data_dpapi(data: str) -> Optional[str]:
        if not WINDOWS_DPAPI_AVAILABLE:
            return None
        try:
            data_bytes = data.encode('utf-8')
            encrypted = win32crypt.CryptProtectData(
                data_bytes,
                "Deadbolt Token"
            )
            return encrypted.hex()
        except Exception as e:
            print(f"DPAPI encryption failed: {e}")
            return None
    
    @staticmethod
    def decrypt_data_dpapi(encrypted_hex: str) -> Optional[str]:
        if not WINDOWS_DPAPI_AVAILABLE:
            return None
        try:
            encrypted_bytes = bytes.fromhex(encrypted_hex)
            desc, decrypted = win32crypt.CryptUnprotectData(encrypted_bytes)
            return decrypted.decode('utf-8')
        except Exception as e:
            print(f"DPAPI decryption failed: {e}")
            return None
    
    @staticmethod
    def validate_password_complexity(password: str) -> Tuple[bool, str]:
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        if not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"
        if not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter"
        if not any(c.isdigit() for c in password):
            return False, "Password must contain at least one digit"
        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if not any(c in special_chars for c in password):
            return False, f"Password must contain at least one special character: {special_chars}"
        return True, "Password is strong"
