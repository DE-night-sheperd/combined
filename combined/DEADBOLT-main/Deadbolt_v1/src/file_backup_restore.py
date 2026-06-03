import os
import shutil
import time
import json
from pathlib import Path
from datetime import datetime
import hashlib


class FileBackupManager:
    def __init__(self, config_dir=None):
        self.config_dir = Path(config_dir) if config_dir else Path.home() / ".deadlock"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.backup_dir = self.config_dir / "backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        self.backup_config_file = self.config_dir / "backup_config.json"
        self.backup_index_file = self.config_dir / "backup_index.json"
        
        self._load_config()
        self._load_backup_index()
        
    def _load_config(self):
        if self.backup_config_file.exists():
            try:
                with open(self.backup_config_file, "r") as f:
                    self.config = json.load(f)
            except:
                self.config = self._default_config()
        else:
            self.config = self._default_config()
            self._save_config()
            
    def _default_config(self):
        return {
            "auto_backup_enabled": True,
            "backup_interval_hours": 24,
            "max_backups_per_file": 5,
            "protected_directories": [
                str(Path.home() / "Documents"),
                str(Path.home() / "Desktop"),
                str(Path.home() / "Pictures"),
                str(Path.home() / "Videos")
            ],
            "protected_extensions": [
                ".docx", ".doc", ".xlsx", ".xls", ".pptx", ".ppt",
                ".pdf", ".txt", ".jpg", ".jpeg", ".png", ".mp4",
                ".zip", ".rar", ".7z", ".psd", ".ai", ".indd"
            ]
        }
        
    def _save_config(self):
        with open(self.backup_config_file, "w") as f:
            json.dump(self.config, f, indent=2)
            
    def _load_backup_index(self):
        if self.backup_index_file.exists():
            try:
                with open(self.backup_index_file, "r") as f:
                    self.backup_index = json.load(f)
            except:
                self.backup_index = {}
        else:
            self.backup_index = {}
            
    def _save_backup_index(self):
        with open(self.backup_index_file, "w") as f:
            json.dump(self.backup_index, f, indent=2)
            
    def _get_file_hash(self, file_path):
        try:
            hasher = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except:
            return None
            
    def _create_backup_name(self, original_path):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        original_name = Path(original_path).name
        return f"{timestamp}_{original_name}"
        
    def backup_file(self, file_path):
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                return False, "File does not exist"
                
            if not file_path.is_file():
                return False, "Not a file"
                
            file_ext = file_path.suffix.lower()
            if file_ext not in self.config["protected_extensions"]:
                return False, "File extension not protected"
                
            file_hash = self._get_file_hash(file_path)
            if not file_hash:
                return False, "Failed to compute file hash"
                
            backup_name = self._create_backup_name(file_path)
            backup_path = self.backup_dir / backup_name
            
            shutil.copy2(file_path, backup_path)
            
            file_key = str(file_path.absolute())
            if file_key not in self.backup_index:
                self.backup_index[file_key] = []
                
            self.backup_index[file_key].append({
                "timestamp": time.time(),
                "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "backup_name": backup_name,
                "file_hash": file_hash,
                "file_size": file_path.stat().st_size
            })
            
            while len(self.backup_index[file_key]) > self.config["max_backups_per_file"]:
                old_backup = self.backup_index[file_key].pop(0)
                old_backup_path = self.backup_dir / old_backup["backup_name"]
                if old_backup_path.exists():
                    old_backup_path.unlink()
                    
            self._save_backup_index()
            
            return True, f"Backup created: {backup_name}"
            
        except Exception as e:
            return False, f"Backup failed: {str(e)}"
            
    def backup_directory(self, dir_path):
        results = []
        dir_path = Path(dir_path)
        
        if not dir_path.exists() or not dir_path.is_dir():
            return results
            
        for item in dir_path.rglob("*"):
            if item.is_file():
                success, msg = self.backup_file(item)
                results.append((str(item), success, msg))
                
        return results
        
    def get_backups(self, file_path):
        file_key = str(Path(file_path).absolute())
        return self.backup_index.get(file_key, [])
        
    def restore_backup(self, file_path, backup_index_pos=0):
        try:
            file_key = str(Path(file_path).absolute())
            backups = self.backup_index.get(file_key, [])
            
            if not backups:
                return False, "No backups found"
                
            if backup_index_pos >= len(backups):
                return False, "Invalid backup index"
                
            backup = backups[backup_index_pos]
            backup_path = self.backup_dir / backup["backup_name"]
            
            if not backup_path.exists():
                return False, "Backup file not found"
                
            original_path = Path(file_path)
            if original_path.exists():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                quarantine_path = self.backup_dir / f"quarantine_{timestamp}_{original_path.name}"
                shutil.move(original_path, quarantine_path)
                
            shutil.copy2(backup_path, original_path)
            
            return True, f"Restored from: {backup['datetime']}"
            
        except Exception as e:
            return False, f"Restore failed: {str(e)}"
            
    def list_all_backups(self):
        return self.backup_index
        
    def delete_all_backups(self):
        try:
            for backup_name in os.listdir(self.backup_dir):
                backup_path = self.backup_dir / backup_name
                if backup_path.is_file():
                    backup_path.unlink()
            self.backup_index = {}
            self._save_backup_index()
            return True, "All backups deleted"
        except Exception as e:
            return False, f"Failed to delete backups: {str(e)}"
            
    def auto_backup(self):
        if not self.config["auto_backup_enabled"]:
            return []
            
        all_results = []
        for dir_path in self.config["protected_directories"]:
            results = self.backup_directory(dir_path)
            all_results.extend(results)
            
        return all_results


if __name__ == "__main__":
    print("=== DEADLOCK FILE BACKUP & RESTORE ===")
    manager = FileBackupManager()
    
    test_file = Path.home() / "Desktop" / "test_backup.txt"
    if not test_file.exists():
        with open(test_file, "w") as f:
            f.write("This is a test file for backup/restore system!")
    
    print("\n1. Testing backup...")
    success, msg = manager.backup_file(test_file)
    print(f"   {msg}")
    
    print("\n2. Listing backups...")
    backups = manager.get_backups(test_file)
    for i, backup in enumerate(backups):
        print(f"   [{i}] {backup['datetime']} - {backup['backup_name']}")
    
    print("\n3. Modifying test file...")
    with open(test_file, "w") as f:
        f.write("This file has been modified!")
    
    print("\n4. Restoring backup...")
    success, msg = manager.restore_backup(test_file, 0)
    print(f"   {msg}")
    
    print("\n5. Verifying restored content...")
    with open(test_file, "r") as f:
        print(f"   Content: {f.read()}")
