import os
import sys
import json
import time
import psutil
import threading
from pathlib import Path
from collections import defaultdict


class SystemActivityMonitor:
    def __init__(self, config_dir=None):
        self.config_dir = Path(config_dir) if config_dir else Path.home() / ".deadlock"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.activity_log_file = self.config_dir / "system_activity.log"
        self.app_usage_file = self.config_dir / "app_usage.json"
        
        self.running = False
        self.monitor_thread = None
        self.lock = threading.Lock()
        
        self.current_processes = {}
        self.app_usage = defaultdict(lambda: {"duration": 0, "last_seen": 0, "count": 0})
        
        self._load_app_usage()
        
    def _load_app_usage(self):
        if self.app_usage_file.exists():
            try:
                with open(self.app_usage_file, "r") as f:
                    data = json.load(f)
                    for app, stats in data.items():
                        self.app_usage[app] = stats
            except:
                pass
    
    def _save_app_usage(self):
        with open(self.app_usage_file, "w") as f:
            json.dump(dict(self.app_usage), f, indent=2)
    
    def _log_activity(self, message):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        with open(self.activity_log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)
        print(f"[Activity Monitor] {message}")
    
    def get_running_applications(self):
        apps = []
        for proc in psutil.process_iter(['pid', 'name', 'exe', 'create_time']):
            try:
                apps.append({
                    "pid": proc.info['pid'],
                    "name": proc.info['name'],
                    "exe": proc.info['exe'],
                    "start_time": proc.info['create_time']
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return apps
    
    def monitor_loop(self):
        last_check = time.time()
        while self.running:
            current_time = time.time()
            delta = current_time - last_check
            last_check = current_time
            
            with self.lock:
                current_procs = {}
                for proc in psutil.process_iter(['pid', 'name', 'exe']):
                    try:
                        key = f"{proc.info['name']}"
                        if key not in self.current_processes:
                            self._log_activity(f"Application started: {proc.info['name']}")
                            self.app_usage[key]["count"] += 1
                        
                        current_procs[key] = True
                        self.app_usage[key]["duration"] += delta
                        self.app_usage[key]["last_seen"] = current_time
                        
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                        pass
                
                for key in list(self.current_processes.keys()):
                    if key not in current_procs:
                        self._log_activity(f"Application closed: {key}")
                
                self.current_processes = current_procs
                
                if int(current_time) % 60 == 0:
                    self._save_app_usage()
            
            time.sleep(1)
    
    def get_app_usage_stats(self):
        return dict(self.app_usage)
    
    def get_activity_log(self, lines=100):
        if self.activity_log_file.exists():
            with open(self.activity_log_file, "r", encoding="utf-8") as f:
                all_lines = f.readlines()
                return all_lines[-lines:]
        return []
    
    def start(self):
        if self.running:
            return
        self.running = True
        self._log_activity("System Activity Monitor started")
        self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
        self.monitor_thread.start()
    
    def stop(self):
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=3)
        self._save_app_usage()
        self._log_activity("System Activity Monitor stopped")


if __name__ == "__main__":
    print("=== DEADLOCK SYSTEM ACTIVITY MONITOR ===")
    monitor = SystemActivityMonitor()
    monitor.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping monitor...")
        monitor.stop()
