import os
import sys
import time
import threading
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from pathlib import Path
from typing import Callable, Optional
import json

sys.path.insert(0, os.path.dirname(__file__))
from security_utils import SecurityUtils
from threat_detector import ThreatDetector

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False

class TokenAuthenticator:
    def __init__(self, config_dir: Path):
        self.config_dir = config_dir
        self.config_file = config_dir / "token_config.json"
        self.hmac_key_file = config_dir / ".hmac_key"
        self.first_launch_file = config_dir / ".first_launch"
        self.token = self._load_or_create_token()
        self.hmac_key = self._load_or_create_hmac_key()
        SecurityUtils.secure_config_directory(config_dir)
        self.is_first_launch = not self.first_launch_file.exists()
        
    def _load_or_create_hmac_key(self) -> bytes:
        if self.hmac_key_file.exists():
            try:
                with open(self.hmac_key_file, 'rb') as f:
                    return f.read()
            except Exception:
                pass
        key = SecurityUtils.generate_hmac_key()
        try:
            with open(self.hmac_key_file, 'wb') as f:
                f.write(key)
        except Exception:
            pass
        return key
        
    def _load_or_create_token(self) -> str:
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    encrypted_token = data.get('encrypted_token')
                    if encrypted_token:
                        decrypted = SecurityUtils.decrypt_data_dpapi(encrypted_token)
                        if decrypted:
                            return decrypted
                    return data.get('token', 'Deadlock2024!')
            except Exception:
                pass
        default_token = "Deadlock2024!"
        self._save_token(default_token)
        return default_token
        
    def _save_token(self, token: str):
        try:
            data = {}
            encrypted = SecurityUtils.encrypt_data_dpapi(token)
            if encrypted:
                data['encrypted_token'] = encrypted
            else:
                data['token'] = token
            with open(self.config_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass
            
    def verify_token(self, input_token: str) -> bool:
        return input_token == self.token
        
    def set_token(self, new_token: str):
        is_valid, msg = SecurityUtils.validate_password_complexity(new_token)
        if not is_valid:
            raise ValueError(msg)
        self.token = new_token
        self._save_token(new_token)
        
    def mark_first_launch_complete(self):
        try:
            with open(self.first_launch_file, 'w') as f:
                f.write('1')
            self.is_first_launch = False
        except Exception:
            pass
            
    def check_peripheral_key(self):
        try:
            from usb_peripheral_key import USBPeripheralKey
            usb_key = USBPeripheralKey(self.config_dir)
            usb_drives = usb_key.get_usb_drives()
            for drive in usb_drives:
                success, msg = usb_key.verify_peripheral_key(drive)
                if success:
                    return True
            return False
        except Exception:
            return False

class FileOperationDialog:
    def __init__(self, file_path: str, operation: str, on_allow: Callable, on_deny: Callable, authenticator: TokenAuthenticator):
        self.file_path = file_path
        self.operation = operation
        self.on_allow = on_allow
        self.on_deny = on_deny
        self.authenticator = authenticator
        self.result = False
        
        self.root = tk.Toplevel()
        self.root.title("DEADLOCK - FILE OPERATION BLOCKED")
        self.root.geometry("600x450")
        self.root.configure(bg="#1a1a2e")
        self.root.attributes('-topmost', True)
        self.root.grab_set()
        
        self.setup_ui()
        
    def setup_ui(self):
        header = tk.Frame(self.root, bg="#aa0000", height=80)
        header.pack(fill=tk.X)
        
        tk.Label(
            header,
            text="⚠️  FILE OPERATION BLOCKED",
            font=("Consolas", 20, "bold"),
            bg="#aa0000",
            fg="#ffffff"
        ).pack(pady=25)
        
        main_frame = tk.Frame(self.root, bg="#1a1a2e", padx=30, pady=30)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(
            main_frame,
            text="Operation Details:",
            font=("Consolas", 14, "bold"),
            bg="#1a1a2e",
            fg="#00ff00"
        ).pack(anchor=tk.W)
        
        info_frame = tk.Frame(main_frame, bg="#0f3460", padx=20, pady=20)
        info_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(
            info_frame,
            text=f"OPERATION: {self.operation.upper()}",
            font=("Consolas", 12),
            bg="#0f3460",
            fg="#ffff00"
        ).pack(anchor=tk.W)
        
        tk.Label(
            info_frame,
            text=f"FILE/FOLDER: {self.file_path}",
            font=("Consolas", 10),
            bg="#0f3460",
            fg="#ffffff"
        ).pack(anchor=tk.W, pady=(10, 0))
        
        tk.Label(
            main_frame,
            text="Enter Level 1 Token Key to Allow:",
            font=("Consolas", 12, "bold"),
            bg="#1a1a2e",
            fg="#00ffff"
        ).pack(anchor=tk.W, pady=(20, 10))
        
        self.token_var = tk.StringVar()
        token_entry = tk.Entry(
            main_frame,
            textvariable=self.token_var,
            font=("Consolas", 14),
            show="*",
            width=30
        )
        token_entry.pack(fill=tk.X, pady=5)
        token_entry.focus()
        
        btn_frame = tk.Frame(main_frame, bg="#1a1a2e")
        btn_frame.pack(fill=tk.X, pady=20)
        
        tk.Button(
            btn_frame,
            text="✅ ALLOW OPERATION",
            command=self.allow,
            bg="#00aa00",
            fg="#ffffff",
            font=("Consolas", 12, "bold"),
            height=2,
            width=20
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="❌ DENY OPERATION",
            command=self.deny,
            bg="#aa0000",
            fg="#ffffff",
            font=("Consolas", 12, "bold"),
            height=2,
            width=20
        ).pack(side=tk.RIGHT, padx=5)
        
    def allow(self):
        token = self.token_var.get()
        if self.authenticator.verify_token(token):
            self.result = True
            self.root.destroy()
            self.on_allow()
        else:
            messagebox.showerror("Error", "Invalid token key!")
            
    def deny(self):
        self.result = False
        self.root.destroy()
        self.on_deny()
        
    def show(self):
        self.root.wait_window()

class FileOperationHandler(FileSystemEventHandler):
    def __init__(self, authenticator: TokenAuthenticator, controller):
        self.authenticator = authenticator
        self.controller = controller
        self.processed_events = set()
        self.threat_detector = ThreatDetector()
        
    def on_modified(self, event):
        if not event.is_directory:
            self._handle_event(event.src_path, "MODIFIED")
            
    def on_created(self, event):
        self._handle_event(event.src_path, "CREATED")
        
    def on_deleted(self, event):
        self._handle_event(event.src_path, "DELETED")
        
    def on_moved(self, event):
        self._handle_event(event.dest_path, f"MOVED to {event.dest_path}")
        
    def _handle_event(self, path: str, operation: str):
        event_key = f"{path}-{operation}-{time.time()}"
        if event_key in self.processed_events:
            return
        self.processed_events.add(event_key)
        if len(self.processed_events) > 1000:
            self.processed_events.clear()
            
        # Check threat detector first!
        is_threat, threat_msg = self.threat_detector.analyze_event(path, operation)
        if is_threat:
            print(f"THREAT DETECTED: {threat_msg} on {path}")
            self._show_block_dialog(path, f"{operation} - {threat_msg}")
            return
            
        rules = self.controller.get_rules()
        should_block = False
        for rule in rules:
            if rule.enabled:
                if os.path.commonpath([rule.path, path]) == rule.path:
                    should_block = True
                    break
                    
        if should_block:
            self._show_block_dialog(path, operation)
            
    def _show_block_dialog(self, path: str, operation: str):
        def on_allow():
            print(f"Allowed: {operation} on {path}")
            
        def on_deny():
            print(f"Denied: {operation} on {path}")
            
        dialog = FileOperationDialog(path, operation, on_allow, on_deny, self.authenticator)
        dialog.show()

class FileOperationMonitor:
    def __init__(self, controller):
        self.controller = controller
        self.config_dir = Path.home() / ".deadlock"
        self.authenticator = TokenAuthenticator(self.config_dir)
        self.observer = None
        self.is_running = False
        
        if WATCHDOG_AVAILABLE:
            self.observer = Observer()
            
    def start(self):
        if not WATCHDOG_AVAILABLE:
            print("Watchdog not available - file monitoring disabled")
            return
            
        if self.is_running:
            return
            
        self.is_running = True
        rules = self.controller.get_rules()
        watched_paths = set()
        for rule in rules:
            if rule.enabled and os.path.exists(rule.path):
                watched_paths.add(rule.path)
                
        for path in watched_paths:
            event_handler = FileOperationHandler(self.authenticator, self.controller)
            self.observer.schedule(event_handler, path, recursive=True)
            
        self.observer.start()
        print("File operation monitor started!")
        
    def stop(self):
        if self.observer and self.is_running:
            self.observer.stop()
            self.observer.join()
            self.is_running = False
            print("File operation monitor stopped!")
