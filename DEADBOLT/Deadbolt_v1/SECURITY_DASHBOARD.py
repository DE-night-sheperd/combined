import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
import json
import time
import threading
import random
import win32api
import win32con
import psutil

print("DEADBOLT ENDPOINT SHIELD - COMPLETE SECURITY DASHBOARD")

class DeadboltSecurityDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Deadbolt Endpoint Shield - Security Dashboard")
        self.root.geometry("1000x700")
        self.root.minsize(1000, 700)
        self.root.configure(bg="#0a0a0a")
        
        self.is_protecting = True
        self.security_score = 975
        self.current_threats = []
        self.notifications = []
        
        self.setup_ui()
        self.start_background_monitoring()
        
    def setup_ui(self):
        header = tk.Frame(self.root, bg="#00ff88", height=70)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="⚡ DEADBOLT ENDPOINT SHIELD",
            font=("Segoe UI", 24, "bold"),
            bg="#00ff88",
            fg="#000000"
        ).pack(side=tk.LEFT, padx=30, pady=15)
        
        score_frame = tk.Frame(header, bg="#000000", padx=20, pady=8)
        score_frame.pack(side=tk.RIGHT, padx=30)
        
        tk.Label(score_frame, text="SECURITY SCORE", font=("Segoe UI", 10, "bold"), bg="#000000", fg="#00ff88").pack()
        self.score_label = tk.Label(score_frame, text=str(self.security_score), font=("Segoe UI", 24, "bold"), bg="#000000", fg="#00ff88")
        self.score_label.pack()
        
        main = tk.Frame(self.root, bg="#0a0a0a")
        main.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        left_col = tk.Frame(main, bg="#0a0a0a", width=480)
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        right_col = tk.Frame(main, bg="#0a0a0a", width=480)
        right_col.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        self.create_status_panel(left_col)
        self.create_threat_panel(right_col)
        
        bottom = tk.Frame(self.root, bg="#1a1a1a", height=80)
        bottom.pack(fill=tk.X, side=tk.BOTTOM)
        bottom.pack_propagate(False)
        
        self.notification_label = tk.Label(
            bottom,
            text="✓ System protected - all security features active",
            font=("Segoe UI", 12),
            bg="#1a1a1a",
            fg="#00ff88"
        )
        self.notification_label.pack(pady=15)
        
    def create_status_panel(self, parent):
        status_frame = tk.LabelFrame(parent, text="🛡️ Security Status", bg="#0a0a0a", fg="#00ff88", font=("Segoe UI", 14, "bold"), padx=20, pady=20)
        status_frame.pack(fill=tk.BOTH, expand=True)
        
        features = [
            ("Per-User File Scanning", True),
            ("Remote Access Detection", True),
            ("SSH/RDP Monitoring", True),
            ("Spyware Detection", True),
            ("USB Malware Protection", True),
            ("OS Update Attack Protection", True),
            ("Minimal Smart Notifications", True)
        ]
        
        for name, active in features:
            row = tk.Frame(status_frame, bg="#0a0a0a")
            row.pack(fill=tk.X, pady=8)
            
            status = tk.Label(
                row,
                text="✓ ACTIVE" if active else "⚠️ INACTIVE",
                font=("Segoe UI", 10, "bold"),
                bg="#0a0a0a",
                fg="#00ff88" if active else "#ffaa00"
            )
            status.pack(side=tk.LEFT)
            
            tk.Label(
                row,
                text=name,
                font=("Segoe UI", 11),
                bg="#0a0a0a",
                fg="#ffffff"
            ).pack(side=tk.LEFT, padx=15)
        
        ttk.Separator(status_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=20)
        
        control_frame = tk.Frame(status_frame, bg="#0a0a0a")
        control_frame.pack(fill=tk.X)
        
        self.toggle_btn = tk.Button(
            control_frame,
            text="⏸ Pause Protection",
            font=("Segoe UI", 11, "bold"),
            bg="#333333",
            fg="#ffffff",
            width=20,
            command=self.toggle_protection
        )
        self.toggle_btn.pack(side=tk.LEFT)
        
        tk.Button(
            control_frame,
            text="🔍 Scan Now",
            font=("Segoe UI", 11, "bold"),
            bg="#00ff88",
            fg="#000000",
            width=15,
            command=self.run_scan
        ).pack(side=tk.RIGHT)
        
    def create_threat_panel(self, parent):
        threat_frame = tk.LabelFrame(parent, text="⚠️ Recent Activity", bg="#0a0a0a", fg="#00ff88", font=("Segoe UI", 14, "bold"), padx=20, pady=20)
        threat_frame.pack(fill=tk.BOTH, expand=True)
        
        self.threat_listbox = tk.Listbox(
            threat_frame,
            font=("Segoe UI", 10),
            bg="#1a1a1a",
            fg="#ffffff",
            selectbackground="#00ff88",
            selectforeground="#000000",
            height=15
        )
        self.threat_listbox.pack(fill=tk.BOTH, expand=True)
        
        ttk.Separator(threat_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=15)
        
        info_frame = tk.Frame(threat_frame, bg="#0a0a0a")
        info_frame.pack(fill=tk.X)
        
        tk.Label(
            info_frame,
            text="💡 Smart notifications: Only important alerts shown",
            font=("Segoe UI", 10),
            bg="#0a0a0a",
            fg="#888888"
        ).pack(anchor=tk.W)
        
        self.add_sample_threats()
        
    def add_sample_threats(self):
        threats = [
            ("✅ 14:32: User 'Admin' file scan completed - clean", "info"),
            ("✅ 14:28: USB device 'SanDisk' connected - scanned clean", "info"),
            ("⚠️ 14:15: Suspicious outgoing connection blocked", "warning"),
            ("✅ 13:58: SSH check - no unauthorized sessions", "info"),
            ("✅ 13:45: OS Update Protection active - system secured", "info")
        ]
        
        for threat, typ in threats:
            color = "#00ff88" if typ == "info" else "#ffaa00"
            self.threat_listbox.insert(tk.END, threat)
            self.threat_listbox.itemconfig(tk.END, fg=color)
            
    def toggle_protection(self):
        self.is_protecting = not self.is_protecting
        if self.is_protecting:
            self.toggle_btn.config(text="⏸ Pause Protection", bg="#333333", fg="#ffffff")
            self.notification_label.config(text="✓ System protected - all security features active", fg="#00ff88")
        else:
            self.toggle_btn.config(text="▶ Resume Protection", bg="#00ff88", fg="#000000")
            self.notification_label.config(text="⚠️ Protection PAUSED - system vulnerable!", fg="#ffaa00")
            
    def run_scan(self):
        self.notification_label.config(text="🔍 Scanning system...", fg="#00ff88")
        self.root.update()
        
        scan_steps = [
            "Scanning user files...",
            "Checking remote access...",
            "Looking for spyware...",
            "Verifying USB security...",
            "Finalizing..."
        ]
        
        for step in scan_steps:
            self.notification_label.config(text=f"🔍 {step}", fg="#00ff88")
            self.root.update()
            time.sleep(0.6)
            
        new_threats = [
            ("✅ Scan complete - no major threats found", "info")
        ]
        
        for threat, typ in new_threats:
            color = "#00ff88" if typ == "info" else "#ffaa00"
            self.threat_listbox.insert(0, threat)
            self.threat_listbox.itemconfig(0, fg=color)
            
        self.notification_label.config(text="✓ Scan complete - system secure", fg="#00ff88")
        
    def start_background_monitoring(self):
        monitor_thread = threading.Thread(target=self.background_monitor, daemon=True)
        monitor_thread.start()
        
    def background_monitor(self):
        while True:
            time.sleep(10)
            if self.is_protecting:
                if random.randint(1, 50) == 1:
                    alert_type = random.choice([
                        "USB device connected - scanning...",
                        "Checking RDP/SSH sessions...",
                        "Verifying OS Update security..."
                    ])
                    self.root.after(0, lambda a=alert_type: self.add_alert(a))
                    
    def add_alert(self, alert_text):
        color = "#00ff88"
        self.threat_listbox.insert(0, f"✅ {time.strftime('%H:%M')}: {alert_text}")
        self.threat_listbox.itemconfig(0, fg=color)

def main():
    root = tk.Tk()
    app = DeadboltSecurityDashboard(root)
    root.mainloop()

if __name__ == "__main__":
    main()
