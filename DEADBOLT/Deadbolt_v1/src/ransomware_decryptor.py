import os
import sys
import json
import time
from pathlib import Path


class RansomwareDecryptor:
    def __init__(self, config_dir=None):
        self.config_dir = Path(config_dir) if config_dir else Path.home() / ".deadlock"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.decryptor_config_file = self.config_dir / "decryptor_config.json"
        self.decryptor_log_file = self.config_dir / "decryptor.log"
        
        self.known_ransomware = {
            ".locky": "Locky",
            ".zepto": "Zepto",
            ".wannacry": "WannaCry",
            ".cryptolocker": "CryptoLocker",
            ".petya": "Petya",
            ".notpetya": "NotPetya"
        }
        
        self._load_config()
        
    def _load_config(self):
        if self.decryptor_config_file.exists():
            try:
                with open(self.decryptor_config_file, "r") as f:
                    self.config = json.load(f)
            except:
                self.config = self._default_config()
                self._save_config()
        else:
            self.config = self._default_config()
            self._save_config()
            
    def _default_config(self):
        return {
            "auto_decrypt": False,
            "backup_before_decrypt": True
        }
        
    def _save_config(self):
        with open(self.decryptor_config_file, "w") as f:
            json.dump(self.config, f, indent=2)
            
    def _log_event(self, message):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        with open(self.decryptor_log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)
        print(f"[Decryptor] {message}")
        
    def identify_ransomware(self, directory):
        directory = Path(directory)
        if not directory.exists():
            return []
            
        ransomware_found = []
        for item in directory.rglob("*"):
            if item.is_file():
                ext = item.suffix.lower()
                if ext in self.known_ransomware:
                    ransomware_found.append({
                        "file": str(item),
                        "ransomware": self.known_ransomware[ext],
                        "extension": ext
                    })
        return ransomware_found
        
    def get_decryptor_status(self):
        return {
            "known_ransomware": list(self.known_ransomware.keys()),
            "config": self.config
        }


if __name__ == "__main__":
    print("=== DEADLOCK RANSOMWARE DECRYPTION TOOLKIT ===")
    decryptor = RansomwareDecryptor()
    print("Known ransomware strains:")
    for ext, name in decryptor.known_ransomware.items():
        print(f"  {ext} - {name}")
