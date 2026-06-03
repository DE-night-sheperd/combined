import os
import sys
import time
import json
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from collections import deque

sys.path.insert(0, os.path.dirname(__file__))
from threat_intelligence import ThreatIntelligenceFeed
from ai_threat_detector import AIThreatDetector


class USBSandboxScanner:
    def __init__(self, config_dir=None):
        self.config_dir = Path(config_dir) if config_dir else Path.home() / ".deadlock"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.usb_config_file = self.config_dir / "usb_sandbox_config.json"
        self.usb_log_file = self.config_dir / "usb_scan.log"
        
        self.threat_feed = ThreatIntelligenceFeed(self.config_dir)
        self.ai_detector = AIThreatDetector(self.config_dir)
        
        self.running = False
        self.monitor_thread = None
        self.known_usbs = set()
        
        self._load_config()
        
    def _load_config(self):
        if self.usb_config_file.exists():
            try:
                with open(self.usb_config_file, "r") as f:
                    self.config = json.load(f)
            except:
                self.config = self._default_config()
                self._save_config()
        else:
            self.config = self._default_config()
            self._save_config()
            
    def _default_config(self):
        return {
            "enabled": True,
            "auto_scan": True,
            "scan_depth": "medium",
            "trusted_usbs": []
        }
        
    def _save_config(self):
        with open(self.usb_config_file, "w") as f:
            json.dump(self.config, f, indent=2)
            
    def _log_event(self, message):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        with open(self.usb_log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)
        print(f"[USB Sandbox] {message}")
        
    def get_usb_drives(self):
        usb_drives = []
        try:
            from string import ascii_uppercase
            import ctypes
            bitmask = ctypes.windll.kernel32.GetLogicalDrives()
            for letter in ascii_uppercase:
                if bitmask & 1:
                    drive = f"{letter}:\\"
                    try:
                        drive_type = ctypes.windll.kernel32.GetDriveTypeW(drive)
                        if drive_type == 2:
                            usb_drives.append(drive)
                    except:
                        pass
                bitmask >>= 1
        except Exception as e:
            self._log_event(f"Error detecting USB drives: {e}")
        return usb_drives
        
    def scan_usb_drive(self, drive_path):
        drive_path = Path(drive_path)
        if not drive_path.exists():
            return False, "Drive not found"
            
        self._log_event(f"Starting scan of {drive_path}")
        
        threats_found = []
        file_count = 0
        threat_count = 0
        
        try:
            for item in drive_path.rglob("*"):
                if item.is_file():
                    file_count += 1
                    
                    result1 = self.threat_feed.check_file_hash(str(item))
                    if result1["is_malicious"]:
                        threats_found.append({
                            "file": str(item),
                            "reason": result1["details"],
                            "severity": "high"
                        })
                        threat_count += 1
                    elif result1["is_suspicious"]:
                        threats_found.append({
                            "file": str(item),
                            "reason": result1["details"],
                            "severity": "medium"
                        })
                    
                    result2 = self.ai_detector.analyze_file_path(str(item))
                    if result2["is_threat"]:
                        reasons = ", ".join(result2["threat_reasons"])
                        threats_found.append({
                            "file": str(item),
                            "reason": reasons,
                            "severity": "high" if result2["threat_score"] >= 80 else "medium"
                        })
                        threat_count += 1
                        
        except Exception as e:
            self._log_event(f"Scan error: {e}")
            
        self._log_event(f"Scan complete - {file_count} files scanned, {threat_count} threats found")
        return True, {
            "file_count": file_count,
            "threat_count": threat_count,
            "threats": threats_found
        }
        
    def show_scan_popup(self, drive_path):
        def on_scan():
            root.destroy()
            self._log_event(f"User approved scan for {drive_path}")
            success, result = self.scan_usb_drive(drive_path)
            if success:
                if result["threat_count"] > 0:
                    threat_msg = f"⚠️  THREATS FOUND!\n\n"
                    threat_msg += f"Files scanned: {result['file_count']}\n"
                    threat_msg += f"Threats detected: {result['threat_count']}\n\n"
                    for threat in result["threats"][:10]:
                        threat_msg += f"- {threat['file']}\n  {threat['reason']}\n"
                    if len(result["threats"]) > 10:
                        threat_msg += f"\n... and {len(result['threats']) - 10} more threats\n"
                    messagebox.showwarning("USB Scan Results", threat_msg)
                else:
                    messagebox.showinfo("USB Scan Results", f"✅ USB Drive Clean!\n\nFiles scanned: {result['file_count']}\nNo threats found.")
            else:
                messagebox.showerror("Scan Error", result)
                
        def on_skip():
            root.destroy()
            self._log_event(f"User skipped scan for {drive_path}")
            messagebox.showinfo("Skipped", "USB access granted without scan.")
            
        root = tk.Tk()
        root.title("DEADLOCK - USB DRIVE DETECTED")
        root.geometry("600x350")
        root.configure(bg="#000000")
        root.resizable(False, False)
        
        tk.Label(
            root,
            text="⚠️  USB DRIVE DETECTED",
            fg="#ffff00",
            bg="#000000",
            font=("Courier New", 18, "bold")
        ).pack(pady=30)
        
        tk.Label(
            root,
            text=f"New USB drive found: {drive_path}",
            fg="#00ff00",
            bg="#000000",
            font=("Courier New", 12)
        ).pack(pady=10)
        
        tk.Label(
            root,
            text="Do you want to scan this USB drive in the sandbox\nbefore granting full access?",
            fg="#ffffff",
            bg="#000000",
            font=("Courier New", 11),
            justify=tk.CENTER
        ).pack(pady=20)
        
        btn_frame = tk.Frame(root, bg="#000000")
        btn_frame.pack(pady=20)
        
        tk.Button(
            btn_frame,
            text="✅ SCAN USB DRIVE",
            command=on_scan,
            bg="#008000",
            fg="#ffffff",
            font=("Courier New", 12, "bold"),
            width=20,
            padx=10,
            pady=5
        ).pack(side=tk.LEFT, padx=20)
        
        tk.Button(
            btn_frame,
            text="⚠️ SKIP SCAN",
            command=on_skip,
            bg="#ff8000",
            fg="#ffffff",
            font=("Courier New", 12, "bold"),
            width=20,
            padx=10,
            pady=5
        ).pack(side=tk.LEFT, padx=20)
        
        root.mainloop()
        
    def monitor_loop(self):
        while self.running:
            current_usbs = set(self.get_usb_drives())
            new_usbs = current_usbs - self.known_usbs
            
            for usb in new_usbs:
                self._log_event(f"New USB detected: {usb}")
                self.show_scan_popup(usb)
                
            self.known_usbs = current_usbs
            time.sleep(2)
            
    def start(self):
        if self.running:
            return
            
        self.running = True
        self.known_usbs = set(self.get_usb_drives())
        self._log_event("USB Sandbox Scanner started")
        self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
        self.monitor_thread.start()
        
    def stop(self):
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=3)
        self._log_event("USB Sandbox Scanner stopped")


if __name__ == "__main__":
    print("=== DEADLOCK USB SANDBOX SCANNER ===")
    scanner = USBSandboxScanner()
    scanner.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping scanner...")
        scanner.stop()
