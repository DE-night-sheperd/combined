import os
import sys
import json
import time
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import psutil
import win32api
import win32con
import win32security
import wmi

print("DEADBOLT ENDPOINT SHIELD - REAL SYSTEM MONITOR")

class RealSystemMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("Deadbolt Endpoint Shield - Real System Monitor")
        self.root.geometry("1100x750")
        self.root.minsize(1100, 750)
        self.root.configure(bg="#0a0a0a")
        
        self.wmi = wmi.WMI()
        self.is_monitoring = True
        
        self.setup_ui()
        self.start_real_monitoring()
        
    def setup_ui(self):
        header = tk.Frame(self.root, bg="#00ff88", height=75)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="⚡ DEADBOLT - REAL SYSTEM PROTECTION",
            font=("Segoe UI", 24, "bold"),
            bg="#00ff88",
            fg="#000000"
        ).pack(side=tk.LEFT, padx=30, pady=18)
        
        main = tk.Frame(self.root, bg="#0a0a0a")
        main.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        left = tk.Frame(main, bg="#0a0a0a", width=520)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        right = tk.Frame(main, bg="#0a0a0a", width=520)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        self.create_activity_log(right)
        self.create_system_info(left)
        
        bottom = tk.Frame(self.root, bg="#1a1a1a", height=100)
        bottom.pack(fill=tk.X, side=tk.BOTTOM)
        bottom.pack_propagate(False)
        
        self.status_label = tk.Label(
            bottom,
            text="🔍 Initializing real system monitoring...",
            font=("Segoe UI", 14),
            bg="#1a1a1a",
            fg="#00ff88"
        )
        self.status_label.pack(pady=20)
        
    def create_system_info(self, parent):
        info_frame = tk.LabelFrame(parent, text="💻 REAL SYSTEM STATUS", bg="#0a0a0a", fg="#00ff88", font=("Segoe UI", 14, "bold"), padx=20, pady=20)
        info_frame.pack(fill=tk.BOTH, expand=True)
        
        self.info_text = tk.Text(
            info_frame,
            font=("Consolas", 10),
            bg="#1a1a1a",
            fg="#00ff88",
            wrap=tk.WORD,
            padx=15,
            pady=15
        )
        self.info_text.pack(fill=tk.BOTH, expand=True)
        
        btn_frame = tk.Frame(info_frame, bg="#0a0a0a")
        btn_frame.pack(fill=tk.X, pady=(15, 0))
        
        tk.Button(
            btn_frame,
            text="🔄 Refresh System Info",
            font=("Segoe UI", 11, "bold"),
            bg="#00ff88",
            fg="#000000",
            width=22,
            command=self.refresh_system_info
        ).pack(side=tk.LEFT)
        
        tk.Button(
            btn_frame,
            text="🛑 Stop Monitoring",
            font=("Segoe UI", 11),
            bg="#333333",
            fg="#ffffff",
            width=20,
            command=self.toggle_monitoring
        ).pack(side=tk.RIGHT)
        
        self.refresh_system_info()
        
    def create_activity_log(self, parent):
        log_frame = tk.LabelFrame(parent, text="📋 REAL-TIME ACTIVITY LOG", bg="#0a0a0a", fg="#00ff88", font=("Segoe UI", 14, "bold"), padx=20, pady=20)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = tk.Text(
            log_frame,
            font=("Consolas", 9),
            bg="#1a1a1a",
            fg="#ffffff",
            wrap=tk.WORD,
            padx=15,
            pady=15
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        self.log("System monitor initialized - collecting real system data")
        
    def log(self, message):
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        
    def refresh_system_info(self):
        self.info_text.delete(1.0, tk.END)
        
        info = []
        info.append("=" * 50)
        info.append("DEADBOLT - REAL SYSTEM INFORMATION")
        info.append("=" * 50)
        info.append("")
        
        info.append("--- OPERATING SYSTEM ---")
        os_info = self.wmi.Win32_OperatingSystem()[0]
        info.append(f"OS Name: {os_info.Name.split('|')[0]}")
        info.append(f"Version: {os_info.Version}")
        info.append(f"System Directory: {os_info.SystemDirectory}")
        info.append("")
        
        info.append("--- CURRENT USER ---")
        info.append(f"Username: {os.environ.get('USERNAME', 'Unknown')}")
        info.append(f"User Profile: {os.environ.get('USERPROFILE', 'Unknown')}")
        info.append("")
        
        info.append("--- RUNNING PROCESSES ---")
        processes = []
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                processes.append(f"PID {proc.info['pid']}: {proc.info['name']}")
            except:
                pass
        info.append(f"Total Processes: {len(processes)}")
        info.append(f"First 20 processes:")
        for p in processes[:20]:
            info.append(f"  {p}")
        info.append("")
        
        info.append("--- NETWORK CONNECTIONS ---")
        connections = psutil.net_connections()
        info.append(f"Active Connections: {len(connections)}")
        info.append("")
        
        info.append("--- USB DEVICES ---")
        usb_devices = self.wmi.Win32_USBControllerDevice()
        info.append(f"USB Controllers/Devices: {len(usb_devices)}")
        info.append("")
        
        info.append("--- SERVICES ---")
        services = list(self.wmi.Win32_Service())
        info.append(f"Total Services: {len(services)}")
        info.append("")
        
        info.append("--- RDP/SSH CHECK ---")
        rdp_running = False
        ssh_running = False
        for proc in psutil.process_iter(['name']):
            try:
                name = proc.info['name'].lower()
                if 'rdp' in name or 'termsrv' in name or 'mstsc' in name:
                    rdp_running = True
                if 'ssh' in name:
                    ssh_running = True
            except:
                pass
        info.append(f"RDP-related processes: {'✓ ACTIVE' if rdp_running else '✗ Not active'}")
        info.append(f"SSH-related processes: {'✓ ACTIVE' if ssh_running else '✗ Not active'}")
        
        self.info_text.insert(1.0, "\n".join(info))
        self.log("System information refreshed from REAL machine")
        
    def toggle_monitoring(self):
        self.is_monitoring = not self.is_monitoring
        if self.is_monitoring:
            self.status_label.config(text="🔍 REAL system monitoring ACTIVE", fg="#00ff88")
        else:
            self.status_label.config(text="⏸ REAL system monitoring PAUSED", fg="#ffaa00")
            
    def start_real_monitoring(self):
        monitor_thread = threading.Thread(target=self.real_system_monitor_loop, daemon=True)
        monitor_thread.start()
        
    def real_system_monitor_loop(self):
        while True:
            time.sleep(3)
            if self.is_monitoring:
                self.check_real_system()
                
    def check_real_system(self):
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    name = proc.info['name'].lower()
                    if 'rdp' in name or 'termsrv' in name or 'mstsc' in name:
                        self.root.after(0, lambda: self.log(f"⚠️  RDP-related process detected: {proc.info['name']} (PID {proc.info['pid']})"))
                    if 'ssh' in name:
                        self.root.after(0, lambda: self.log(f"⚠️  SSH-related process detected: {proc.info['name']} (PID {proc.info['pid']})"))
                except:
                    pass
                    
            usb_devices = self.wmi.Win32_USBControllerDevice()
            if len(usb_devices) > 5:
                self.root.after(0, lambda: self.log(f"💡 USB devices detected: {len(usb_devices)}"))
                
        except Exception as e:
            pass

def main():
    root = tk.Tk()
    app = RealSystemMonitor(root)
    root.mainloop()

if __name__ == "__main__":
    main()
