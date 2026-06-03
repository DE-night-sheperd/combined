import os
import sys
import json
import time
import threading
import subprocess
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))
from security_monitor import DeadlockSecurityMonitor


class IncidentResponseManager:
    def __init__(self, config_dir=None):
        self.config_dir = Path(config_dir) if config_dir else Path.home() / ".deadlock"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.ir_config_file = self.config_dir / "incident_response_config.json"
        self.ir_log_file = self.config_dir / "incident_response.log"
        
        self.security_monitor = DeadlockSecurityMonitor()
        self.lock = threading.Lock()
        
        self._load_config()
        
    def _load_config(self):
        if self.ir_config_file.exists():
            try:
                with open(self.ir_config_file, "r") as f:
                    self.config = json.load(f)
            except:
                self.config = self._default_config()
                self._save_config()
        else:
            self.config = self._default_config()
            self._save_config()
            
    def _default_config(self):
        return {
            "auto_isolate": True,
            "auto_notify": False,
            "notify_email": "",
            "isolation_actions": [
                "disable_wifi",
                "disable_hotspot",
                "lock_system"
            ]
        }
        
    def _save_config(self):
        with open(self.ir_config_file, "w") as f:
            json.dump(self.config, f, indent=2)
            
    def _log_event(self, message):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        with open(self.ir_log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)
        print(f"[Incident Response] {message}")
        
    def trigger_incident_response(self, incident_type, severity, details):
        self._log_event(f"INCIDENT TRIGGERED: {incident_type} (Severity: {severity})")
        self._log_event(f"Details: {details}")
        
        if self.config["auto_isolate"]:
            self.isolate_device()
            
        if self.config["auto_notify"] and self.config["notify_email"]:
            self.send_notification(incident_type, severity, details)
            
    def isolate_device(self):
        with self.lock:
            self._log_event("Starting device isolation...")
            
            if "disable_wifi" in self.config["isolation_actions"]:
                self.security_monitor.disable_wifi()
                
            if "disable_hotspot" in self.config["isolation_actions"]:
                self.security_monitor.disable_hotspot()
                
            if "disable_microphone" in self.config["isolation_actions"]:
                self.security_monitor.disable_microphone()
                
            if "disable_camera" in self.config["isolation_actions"]:
                self.security_monitor.disable_camera()
                
            if "lock_system" in self.config["isolation_actions"]:
                self.security_monitor.lock_system()
                
            self._log_event("Device isolation complete")
            
    def send_notification(self, incident_type, severity, details):
        self._log_event(f"Notification would be sent to {self.config['notify_email']}")
        
    def get_incident_response_status(self):
        return {
            "auto_isolate": self.config["auto_isolate"],
            "auto_notify": self.config["auto_notify"],
            "notify_email": self.config["notify_email"],
            "isolation_actions": self.config["isolation_actions"]
        }


if __name__ == "__main__":
    print("=== DEADLOCK INCIDENT RESPONSE MANAGER ===")
    irm = IncidentResponseManager()
    
    print("\nCurrent configuration:")
    status = irm.get_incident_response_status()
    for key, value in status.items():
        print(f"  {key}: {value}")
