import os
import sys
import time
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional
from collections import deque

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

class AISecurityEngine:
    def __init__(self, config_dir: Path):
        self.config_dir = config_dir
        self.model_file = config_dir / "ai_model.json"
        self.behavior_log = config_dir / "ai_behavior_log.json"
        
        self.operation_history = deque(maxlen=1000)
        self.baseline_profile = self._load_or_create_baseline()
        self.suspicious_patterns = self._load_suspicious_patterns()
        
    def _load_or_create_baseline(self) -> Dict[str, Any]:
        if self.model_file.exists():
            try:
                with open(self.model_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        baseline = {
            "normal_operations": {
                "read": 0.7,
                "write": 0.2,
                "delete": 0.05,
                "rename": 0.05
            },
            "hourly_pattern": [0.1]*24,
            "suspicious_threshold": 0.7,
            "version": "1.0"
        }
        self._save_baseline(baseline)
        return baseline
        
    def _save_baseline(self, baseline: Dict[str, Any]):
        try:
            with open(self.model_file, 'w') as f:
                json.dump(baseline, f, indent=2)
        except Exception:
            pass
            
    def _load_suspicious_patterns(self) -> List[str]:
        return [
            "批量删除", "mass delete",
            "批量复制", "mass copy",
            "移动到USB", "move to usb",
            "复制到USB", "copy to usb",
            "加密", "encrypt",
            "压缩", "compress",
            "rar", "zip", "7z"
        ]
        
    def log_operation(self, path: str, operation: str, timestamp: float = None):
        if timestamp is None:
            timestamp = time.time()
            
        entry = {
            "path": path,
            "operation": operation,
            "timestamp": timestamp,
            "hour": time.localtime(timestamp).tm_hour
        }
        self.operation_history.append(entry)
        self._update_baseline(entry)
        
    def _update_baseline(self, entry: Dict[str, Any]):
        op = entry["operation"].lower()
        if "read" in op:
            self.baseline_profile["normal_operations"]["read"] = \
                (self.baseline_profile["normal_operations"]["read"] * 0.99) + 0.01
        elif "write" in op or "create" in op:
            self.baseline_profile["normal_operations"]["write"] = \
                (self.baseline_profile["normal_operations"]["write"] * 0.99) + 0.01
        elif "delete" in op or "remove" in op:
            self.baseline_profile["normal_operations"]["delete"] = \
                (self.baseline_profile["normal_operations"]["delete"] * 0.99) + 0.01
        elif "rename" in op or "move" in op:
            self.baseline_profile["normal_operations"]["rename"] = \
                (self.baseline_profile["normal_operations"]["rename"] * 0.99) + 0.01
                
        hour = entry["hour"]
        for i in range(24):
            if i == hour:
                self.baseline_profile["hourly_pattern"][i] = \
                    (self.baseline_profile["hourly_pattern"][i] * 0.99) + 0.01
            else:
                self.baseline_profile["hourly_pattern"][i] *= 0.99
                
        self._save_baseline(self.baseline_profile)
        
    def analyze_operation(self, path: str, operation: str) -> Dict[str, Any]:
        result = {
            "suspicious": False,
            "risk_score": 0.0,
            "flags": [],
            "recommendation": "allow"
        }
        
        path_lower = path.lower()
        op_lower = operation.lower()
        
        for pattern in self.suspicious_patterns:
            if pattern in path_lower or pattern in op_lower:
                result["flags"].append(f"Suspicious pattern: {pattern}")
                result["risk_score"] += 0.3
                
        usb_keywords = ["usb", "removable", "d:", "e:", "f:", "g:"]
        for kw in usb_keywords:
            if kw in path_lower:
                result["flags"].append("Possible USB/external drive access")
                result["risk_score"] += 0.4
                
        recent_ops = list(self.operation_history)[-50:]
        delete_count = sum(1 for op in recent_ops if "delete" in op["operation"].lower())
        if delete_count > 10:
            result["flags"].append(f"High delete rate: {delete_count}/50")
            result["risk_score"] += 0.3
            
        if result["risk_score"] >= self.baseline_profile["suspicious_threshold"]:
            result["suspicious"] = True
            result["recommendation"] = "block"
        elif result["risk_score"] >= 0.4:
            result["recommendation"] = "authenticate"
            
        return result
        
    def get_file_hash(self, path: str) -> Optional[str]:
        try:
            sha256_hash = hashlib.sha256()
            with open(path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception:
            return None
