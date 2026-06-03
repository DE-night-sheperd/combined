import os
import json
import hashlib
import subprocess
import threading
import time
from pathlib import Path


class ApplicationWhitelistManager:
    def __init__(self, config_dir=None):
        self.config_dir = Path(config_dir) if config_dir else Path.home() / ".deadlock"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.whitelist_file = self.config_dir / "app_whitelist.json"
        self.blocked_file = self.config_dir / "app_blocked.json"
        self.log_file = self.config_dir / "app_control.log"
        
        self.running = False
        self.monitor_thread = None
        self.lock = threading.Lock()
        
        self._load_whitelist()
        self._load_blocked()
        
    def _load_whitelist(self):
        if self.whitelist_file.exists():
            try:
                with open(self.whitelist_file, "r") as f:
                    self.whitelist = json.load(f)
            except:
                self.whitelist = self._default_whitelist()
                self._save_whitelist()
        else:
            self.whitelist = self._default_whitelist()
            self._save_whitelist()
            
    def _default_whitelist(self):
        system32 = Path(os.environ.get("SystemRoot", "C:\\Windows")) / "System32"
        program_files = Path(os.environ.get("ProgramFiles", "C:\\Program Files"))
        program_files_x86 = Path(os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)"))
        
        return {
            "enabled": True,
            "allowed_paths": [
                str(system32),
                str(program_files),
                str(program_files_x86)
            ],
            "allowed_hashes": [],
            "allowed_signers": []
        }
        
    def _save_whitelist(self):
        with open(self.whitelist_file, "w") as f:
            json.dump(self.whitelist, f, indent=2)
            
    def _load_blocked(self):
        if self.blocked_file.exists():
            try:
                with open(self.blocked_file, "r") as f:
                    self.blocked = json.load(f)
            except:
                self.blocked = {"blocked_hashes": [], "blocked_paths": []}
                self._save_blocked()
        else:
            self.blocked = {"blocked_hashes": [], "blocked_paths": []}
            self._save_blocked()
            
    def _save_blocked(self):
        with open(self.blocked_file, "w") as f:
            json.dump(self.blocked, f, indent=2)
            
    def _log_event(self, message):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)
        print(f"[App Whitelist] {message}")
        
    def _get_file_hash(self, file_path):
        try:
            hasher = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except:
            return None
            
    def is_allowed(self, file_path):
        if not self.whitelist["enabled"]:
            return True
            
        file_path = Path(file_path).absolute()
        
        if not file_path.exists():
            return False
            
        if not file_path.is_file():
            return True
            
        file_ext = file_path.suffix.lower()
        if file_ext not in [".exe", ".bat", ".cmd", ".com", ".scr", ".ps1", ".vbs", ".js"]:
            return True
            
        file_hash = self._get_file_hash(file_path)
        if file_hash and file_hash in self.blocked["blocked_hashes"]:
            self._log_event(f"BLOCKED (hash): {file_path}")
            return False
            
        if str(file_path) in self.blocked["blocked_paths"]:
            self._log_event(f"BLOCKED (path): {file_path}")
            return False
            
        if file_hash and file_hash in self.whitelist["allowed_hashes"]:
            return True
            
        for allowed_path in self.whitelist["allowed_paths"]:
            allowed_path = Path(allowed_path)
            try:
                if file_path.is_relative_to(allowed_path):
                    return True
            except:
                pass
                
        self._log_event(f"BLOCKED (unknown): {file_path}")
        return False
        
    def add_to_whitelist(self, file_path):
        file_path = Path(file_path).absolute()
        if not file_path.exists() or not file_path.is_file():
            return False, "File not found"
            
        file_hash = self._get_file_hash(file_path)
        if file_hash and file_hash not in self.whitelist["allowed_hashes"]:
            self.whitelist["allowed_hashes"].append(file_hash)
            self._save_whitelist()
            self._log_event(f"ADDED TO WHITELIST: {file_path}")
            return True, f"Added: {file_path}"
            
        return False, "Already in whitelist"
        
    def add_path_to_whitelist(self, dir_path):
        dir_path = Path(dir_path).absolute()
        if not dir_path.exists() or not dir_path.is_dir():
            return False, "Directory not found"
            
        dir_str = str(dir_path)
        if dir_str not in self.whitelist["allowed_paths"]:
            self.whitelist["allowed_paths"].append(dir_str)
            self._save_whitelist()
            self._log_event(f"PATH ADDED TO WHITELIST: {dir_str}")
            return True, f"Path added: {dir_str}"
            
        return False, "Path already in whitelist"
        
    def block_application(self, file_path):
        file_path = Path(file_path).absolute()
        if not file_path.exists() or not file_path.is_file():
            return False, "File not found"
            
        file_hash = self._get_file_hash(file_path)
        if file_hash:
            if file_hash not in self.blocked["blocked_hashes"]:
                self.blocked["blocked_hashes"].append(file_hash)
        if str(file_path) not in self.blocked["blocked_paths"]:
            self.blocked["blocked_paths"].append(str(file_path))
            
        self._save_blocked()
        self._log_event(f"BLOCKED APP: {file_path}")
        return True, f"Blocked: {file_path}"
        
    def enable_whitelist(self):
        self.whitelist["enabled"] = True
        self._save_whitelist()
        self._log_event("Application whitelist ENABLED")
        return True
        
    def disable_whitelist(self):
        self.whitelist["enabled"] = False
        self._save_whitelist()
        self._log_event("Application whitelist DISABLED")
        return True
        
    def get_whitelist_status(self):
        return {
            "enabled": self.whitelist["enabled"],
            "allowed_paths_count": len(self.whitelist["allowed_paths"]),
            "allowed_hashes_count": len(self.whitelist["allowed_hashes"]),
            "blocked_hashes_count": len(self.blocked["blocked_hashes"]),
            "blocked_paths_count": len(self.blocked["blocked_paths"])
        }


if __name__ == "__main__":
    print("=== DEADLOCK APPLICATION WHITELISTING ===")
    manager = ApplicationWhitelistManager()
    
    print("\nCurrent status:")
    status = manager.get_whitelist_status()
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    test_exe = Path(os.environ.get("SystemRoot", "C:\\Windows")) / "System32" / "notepad.exe"
    if test_exe.exists():
        print(f"\nChecking {test_exe}...")
        allowed = manager.is_allowed(test_exe)
        print(f"  Allowed: {allowed}")
