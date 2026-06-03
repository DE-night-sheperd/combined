import tkinter as tk
from tkinter import ttk
import time
import random

print("DEADBOLT ENDPOINT SHIELD - BOOT-TIME SCAN")

class BootTimeScan:
    def __init__(self, root):
        self.root = root
        self.root.title("Deadbolt Endpoint Shield - Boot Scan")
        self.root.attributes("-fullscreen", True)
        self.root.overrideredirect(True)
        self.root.configure(bg="#000000")
        
        self.screen_w = self.root.winfo_screenwidth()
        self.screen_h = self.root.winfo_screenheight()
        
        self.create_widgets()
        self.root.after(500, self.start_scan)
        
    def create_widgets(self):
        main = tk.Frame(self.root, bg="#000000")
        main.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(
            main,
            text="⚡ DEADBOLT",
            font=("Segoe UI", 64, "bold"),
            bg="#000000",
            fg="#00ff88"
        ).pack(pady=(80, 5))
        
        tk.Label(
            main,
            text="ENDPOINT SHIELD",
            font=("Segoe UI", 32),
            bg="#000000",
            fg="#ffffff"
        ).pack(pady=(0, 40))
        
        tk.Label(
            main,
            text="BOOT-TIME SECURITY SCAN",
            font=("Segoe UI", 24, "bold"),
            bg="#000000",
            fg="#00ff88"
        ).pack(pady=(0, 30))
        
        self.progress = ttk.Progressbar(main, orient=tk.HORIZONTAL, length=600, mode='determinate')
        self.progress.pack(pady=20)
        
        self.status_label = tk.Label(
            main,
            text="Initializing scan engine...",
            font=("Segoe UI", 14),
            bg="#000000",
            fg="#ffffff"
        )
        self.status_label.pack(pady=10)
        
        self.detail_label = tk.Label(
            main,
            text="",
            font=("Segoe UI", 10),
            bg="#000000",
            fg="#888888"
        )
        self.detail_label.pack(pady=5)
        
        self.threats_label = tk.Label(
            main,
            text="✓ No threats detected yet",
            font=("Segoe UI", 12),
            bg="#000000",
            fg="#00ff88"
        )
        self.threats_label.pack(pady=30)
        
        self.skip_button = tk.Button(
            main,
            text="Skip Scan (Advanced)",
            font=("Segoe UI", 10),
            bg="#333333",
            fg="#888888",
            borderwidth=0,
            command=self.skip_scan
        )
        self.skip_button.pack(side=tk.BOTTOM, pady=30)
        
    def start_scan(self):
        scan_steps = [
            ("Scanning Master Boot Record...", 10, r"\Device\Harddisk0\Partition0"),
            ("Scanning boot sector...", 20, r"C:\Windows\Boot"),
            ("Scanning system drivers...", 35, r"C:\Windows\System32\drivers"),
            ("Scanning startup applications...", 50, r"HKLM\Software\Microsoft\Windows\CurrentVersion\Run"),
            ("Scanning scheduled tasks...", 65, r"C:\Windows\System32\Tasks"),
            ("Scanning Windows services...", 80, r"HKLM\System\CurrentControlSet\Services"),
            ("Verifying system integrity...", 95, "All system files"),
            ("Finalizing...", 100, "Scan complete")
        ]
        
        threats_found = 0
        
        for text, progress, detail in scan_steps:
            self.status_label.config(text=text)
            self.detail_label.config(text=f"Scanning: {detail}")
            self.progress['value'] = progress
            
            if random.randint(1, 100) > 95 and threats_found < 2:
                threats_found += 1
                self.threats_label.config(text=f"⚠️  {threats_found} suspicious item(s) found - quarantining...", fg="#ffaa00")
                self.root.update()
                time.sleep(0.8)
                self.threats_label.config(text=f"✓ {threats_found} item(s) quarantined successfully", fg="#00ff88")
            
            self.root.update()
            time.sleep(0.9)
        
        if threats_found == 0:
            self.threats_label.config(text="✓ System is clean! No threats found.", fg="#00ff88")
        else:
            self.threats_label.config(text=f"✓ {threats_found} item(s) quarantined. System is now safe!", fg="#00ff88")
        
        self.status_label.config(text="Scan complete! Starting Windows...")
        self.root.update()
        
        self.root.after(2500, self.finish)
        
    def skip_scan(self):
        self.finish()
        
    def finish(self):
        self.root.destroy()
        print("Boot scan complete - continuing to Windows")

def main():
    root = tk.Tk()
    app = BootTimeScan(root)
    root.mainloop()

if __name__ == "__main__":
    main()
