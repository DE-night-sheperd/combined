import time
from collections import deque
from pathlib import Path
from typing import List, Dict, Tuple

# Known ransomware extensions
RANSOMWARE_EXTENSIONS = [
    ".locky", ".zepto", ".odin", ".cerber", ".teslacrypt",
    ".xtbl", ".onion", ".aaa", ".abc", ".xyz", ".zzz",
    ".crypto", ".cryp1", ".cry", ".crypt", ".encrypt",
    ".encrypted", ".ransom", ".pay", ".wallet", ".wannacry",
    ".wcry", ".lock", ".locked", ".klock", ".k1ck", ".k3y"
]

# Suspicious file operations thresholds
MAX_FILE_MODIFICATIONS_PER_SECOND = 50
MAX_FILE_CREATIONS_PER_SECOND = 30
MAX_FILE_RENAMES_PER_SECOND = 20

class ThreatDetector:
    def __init__(self):
        self.file_modifications: deque = deque(maxlen=1000)
        self.file_creations: deque = deque(maxlen=1000)
        self.file_renames: deque = deque(maxlen=1000)
        self.ransomware_extensions = RANSOMWARE_EXTENSIONS
        
    def check_ransomware_extension(self, file_path: str) -> Tuple[bool, str]:
        path_obj = Path(file_path)
        ext = path_obj.suffix.lower()
        
        if ext in self.ransomware_extensions:
            return True, f"Suspicious ransomware extension detected: {ext}"
        return False, ""
        
    def check_mass_file_operations(self) -> Tuple[bool, str]:
        now = time.time()
        
        # Clean old timestamps
        while self.file_modifications and (now - self.file_modifications[0]) > 1:
            self.file_modifications.popleft()
        while self.file_creations and (now - self.file_creations[0]) > 1:
            self.file_creations.popleft()
        while self.file_renames and (now - self.file_renames[0]) > 1:
            self.file_renames.popleft()
            
        mod_count = len(self.file_modifications)
        create_count = len(self.file_creations)
        rename_count = len(self.file_renames)
        
        if mod_count > MAX_FILE_MODIFICATIONS_PER_SECOND:
            return True, f"High file modification rate: {mod_count}/sec"
        if create_count > MAX_FILE_CREATIONS_PER_SECOND:
            return True, f"High file creation rate: {create_count}/sec"
        if rename_count > MAX_FILE_RENAMES_PER_SECOND:
            return True, f"High file rename rate: {rename_count}/sec"
            
        return False, ""
        
    def log_modification(self):
        self.file_modifications.append(time.time())
        
    def log_creation(self):
        self.file_creations.append(time.time())
        
    def log_rename(self):
        self.file_renames.append(time.time())
        
    def analyze_event(self, file_path: str, operation: str) -> Tuple[bool, str]:
        # Check ransomware extension first
        is_ransom, ransom_msg = self.check_ransomware_extension(file_path)
        if is_ransom:
            return True, ransom_msg
            
        # Log the operation
        if operation == "MODIFIED":
            self.log_modification()
        elif operation == "CREATED":
            self.log_creation()
        elif "MOVED" in operation:
            self.log_rename()
            
        # Check mass operations
        is_suspicious, mass_msg = self.check_mass_file_operations()
        if is_suspicious:
            return True, mass_msg
            
        return False, ""
