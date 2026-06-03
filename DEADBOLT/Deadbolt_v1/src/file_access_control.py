import os
import json
import time
import threading
from pathlib import Path
from typing import Dict, List, Set, Optional

try:
    from driver_connector import DriverConnector
    DRIVER_AVAILABLE = True
except ImportError:
    DRIVER_AVAILABLE = False

try:
    from windows_permissions import WindowsFilePermissionController
    WINDOWS_PERMISSIONS_AVAILABLE = True
except ImportError:
    WINDOWS_PERMISSIONS_AVAILABLE = False

class FileAccessRule:
    def __init__(self, path: str, rule_type: str, enabled: bool = True, description: str = ""):
        self.path = os.path.abspath(path)
        self.rule_type = rule_type  # 'block_read', 'block_write', 'block_delete', 'block_rename', 'block_access'
        self.enabled = enabled
        self.description = description
        self.created_at = time.time()
    
    def to_dict(self) -> Dict:
        return {
            "path": self.path,
            "rule_type": self.rule_type,
            "enabled": self.enabled,
            "description": self.description,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'FileAccessRule':
        rule = cls(
            path=data["path"],
            rule_type=data["rule_type"],
            enabled=data["enabled"],
            description=data["description"]
        )
        rule.created_at = data["created_at"]
        return rule
    
    def get_driver_rule_type(self) -> int:
        mapping = {
            'block_access': 0,
            'block_read': 1,
            'block_write': 2,
            'block_delete': 3,
            'block_rename': 4
        }
        return mapping.get(self.rule_type, 0)

class FileAccessController:
    def __init__(self, config_dir: Optional[str] = None):
        if config_dir is None:
            config_dir = Path.home() / ".deadbolt"
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        self.rules_file = self.config_dir / "file_access_rules.json"
        self.rules: List[FileAccessRule] = []
        self.lock = threading.Lock()
        self.driver_connector = None
        self.windows_permissions = None
        
        if WINDOWS_PERMISSIONS_AVAILABLE:
            try:
                self.windows_permissions = WindowsFilePermissionController()
                print("Windows permission controller initialized!")
            except Exception as e:
                print(f"Failed to initialize Windows permissions: {e}")
                self.windows_permissions = None
        
        if DRIVER_AVAILABLE:
            try:
                self.driver_connector = DriverConnector()
                self.driver_connector.connect()
                print("Connected to Deadbolt minifilter driver!")
            except Exception as e:
                print(f"Failed to connect to driver: {e}")
                self.driver_connector = None
        
        self.load_rules()
        
        if self.driver_connector:
            self.push_rules_to_driver()
            
    def apply_windows_permissions(self, rule: FileAccessRule):
        if not self.windows_permissions:
            return False
            
        if not rule.enabled:
            return False
            
        try:
            if rule.rule_type == "block_access":
                return self.windows_permissions.block_access(rule.path)
            elif rule.rule_type == "block_write":
                return self.windows_permissions.block_write(rule.path)
            elif rule.rule_type == "block_delete":
                return self.windows_permissions.block_delete(rule.path)
            return True
        except Exception as e:
            print(f"Error applying Windows permissions: {e}")
            return False
    
    def push_rules_to_driver(self):
        if not self.driver_connector:
            return
        
        try:
            self.driver_connector.clear_rules()
            for rule in self.rules:
                if rule.enabled:
                    nt_path = "\\Device\\HarddiskVolume" + rule.path.replace("\\", "\\")
                    if rule.path[1] == ":":
                        drive = rule.path[0].upper()
                        nt_path = f"\\DosDevices\\{drive}:{rule.path[2:]}"
                    
                    self.driver_connector.add_rule(
                        rule.path,
                        rule.get_driver_rule_type(),
                        rule.enabled
                    )
            print(f"Pushed {len([r for r in self.rules if r.enabled])} rules to driver")
        except Exception as e:
            print(f"Error pushing rules to driver: {e}")
    
    def load_rules(self):
        with self.lock:
            if self.rules_file.exists():
                try:
                    with open(self.rules_file, 'r') as f:
                        data = json.load(f)
                        self.rules = [FileAccessRule.from_dict(r) for r in data]
                except Exception:
                    self.rules = []
            else:
                self.rules = []
    
    def save_rules(self):
        with self.lock:
            try:
                with open(self.rules_file, 'w') as f:
                    json.dump([r.to_dict() for r in self.rules], f, indent=2)
            except Exception as e:
                print(f"Error saving rules: {e}")
    
    def add_rule(self, rule: FileAccessRule) -> bool:
        with self.lock:
            self.rules.append(rule)
            self.save_rules()
        
        if self.windows_permissions and rule.enabled:
            self.apply_windows_permissions(rule)
            
        if self.driver_connector:
            self.push_rules_to_driver()
        return True
    
    def remove_rule(self, index: int) -> bool:
        with self.lock:
            if 0 <= index < len(self.rules):
                del self.rules[index]
                self.save_rules()
                if self.driver_connector:
                    self.push_rules_to_driver()
                return True
        return False
    
    def update_rule(self, index: int, **kwargs) -> bool:
        with self.lock:
            if 0 <= index < len(self.rules):
                rule = self.rules[index]
                if 'path' in kwargs:
                    rule.path = kwargs['path']
                if 'rule_type' in kwargs:
                    rule.rule_type = kwargs['rule_type']
                if 'enabled' in kwargs:
                    rule.enabled = kwargs['enabled']
                if 'description' in kwargs:
                    rule.description = kwargs['description']
                self.save_rules()
                if self.driver_connector:
                    self.push_rules_to_driver()
                return True
        return False
    
    def get_rules(self) -> List[FileAccessRule]:
        with self.lock:
            return list(self.rules)
    
    def check_path_matches_rule(self, target_path: str, rule: FileAccessRule) -> bool:
        if not rule.enabled:
            return False
        rule_path = rule.path
        target_path = os.path.abspath(target_path)
        
        if os.path.commonpath([rule_path, target_path]) == rule_path:
            return True
        return False
    
    def should_block_operation(self, target_path: str, operation: str) -> bool:
        """operation: 'read', 'write', 'delete', 'rename', 'access'"""
        with self.lock:
            for rule in self.rules:
                if self.check_path_matches_rule(target_path, rule):
                    if operation == 'read' and rule.rule_type == 'block_read':
                        return True
                    if operation == 'write' and rule.rule_type == 'block_write':
                        return True
                    if operation == 'delete' and rule.rule_type == 'block_delete':
                        return True
                    if operation == 'rename' and rule.rule_type == 'block_rename':
                        return True
                    if rule.rule_type == 'block_access':
                        return True
        return False

class FileAccessMonitor:
    def __init__(self, controller: FileAccessController):
        self.controller = controller
        self.is_monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.log_file = controller.config_dir / "file_access_logs.json"
        self.logs: List[Dict] = []
    
    def log_attempt(self, path: str, operation: str, blocked: bool):
        log_entry = {
            "timestamp": time.time(),
            "path": path,
            "operation": operation,
            "blocked": blocked
        }
        self.logs.append(log_entry)
        try:
            if self.log_file.exists():
                with open(self.log_file, 'r') as f:
                    existing_logs = json.load(f)
            else:
                existing_logs = []
            existing_logs.append(log_entry)
            with open(self.log_file, 'w') as f:
                json.dump(existing_logs[-1000:], f)  # Keep last 1000 logs
        except Exception:
            pass
    
    def get_logs(self) -> List[Dict]:
        if self.log_file.exists():
            try:
                with open(self.log_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return []
