import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
import os
import sys
from pathlib import Path

# Import our modules
sys.path.insert(0, str(Path(__file__).parent))

class DeadboltSandbox:
    def __init__(self, root):
        self.root = root
        self.root.title("DEADBOLT SANDBOX & CONTROL CENTER")
        self.root.geometry("1200x800")
        self.root.configure(bg="#0a0a1a")
        
        self.modules = {
            "monitor": {"status": "Ready", "color": "#00ff00"},
            "zip_bomb": {"status": "Ready", "color": "#00ff00"},
            "ransomware": {"status": "Ready", "color": "#00ff00"},
            "threat_mitigation": {"status": "Ready", "color": "#00ff00"},
            "kernel_driver": {"status": "Not Loaded", "color": "#ffaa00"},
            "file_minifilter": {"status": "Not Loaded", "color": "#ffaa00"}
        }
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main container
        main = tk.Frame(self.root, bg="#0a0a1a")
        main.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        header = tk.Frame(main, bg="#1a1a3a", height=80)
        header.pack(fill=tk.X, pady=(0,10))
        
        tk.Label(
            header,
            text="🔒 DEADBOLT SANDBOX & CONTROL CENTER",
            font=("Consolas", 28, "bold"),
            bg="#1a1a3a",
            fg="#00ff00"
        ).pack(pady=15)
        
        # Split into left and right panels
        panes = tk.PanedWindow(main, orient=tk.HORIZONTAL, bg="#0a0a1a")
        panes.pack(fill=tk.BOTH, expand=True)
        
        # Left: System Architecture Map
        left_frame = tk.Frame(panes, bg="#1a1a2a", width=600)
        panes.add(left_frame, minsize=400)
        
        tk.Label(
            left_frame,
            text="SYSTEM ARCHITECTURE MAP",
            font=("Consolas", 14, "bold"),
            bg="#1a1a2a",
            fg="#00ffff"
        ).pack(pady=10)
        
        canvas = tk.Canvas(left_frame, bg="#0a0a0a", highlightthickness=0)
        canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.draw_architecture(canvas)
        
        # Right: Control Panel & Logs
        right_frame = tk.Frame(panes, bg="#1a1a2a")
        panes.add(right_frame, minsize=400)
        
        # Module Status Grid
        status_frame = tk.LabelFrame(
            right_frame, 
            text="MODULE STATUS", 
            bg="#1a1a2a",
            fg="#00ff00",
            font=("Consolas", 11, "bold"),
            padx=10,
            pady=10
        )
        status_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.status_labels = {}
        row = 0
        module_info = [
            ("📂 File Monitor", "monitor"),
            ("📦 Zip Bomb Detector", "zip_bomb"),
            ("🔒 Ransomware Shield", "ransomware"),
            ("🛡️ Threat Mitigation", "threat_mitigation"),
            ("💻 Kernel Driver", "kernel_driver"),
            ("📄 Minifilter Driver", "file_minifilter")
        ]
        
        for name, key in module_info:
            lbl_name = tk.Label(
                status_frame,
                text=name,
                bg="#1a1a2a",
                fg="#ffffff",
                font=("Consolas", 10),
                anchor=tk.W
            )
            lbl_name.grid(row=row, column=0, sticky=tk.W, pady=5)
            
            lbl_status = tk.Label(
                status_frame,
                text=self.modules[key]["status"],
                bg="#1a1a2a",
                fg=self.modules[key]["color"],
                font=("Consolas", 10, "bold")
            )
            lbl_status.grid(row=row, column=1, sticky=tk.W, padx=20)
            self.status_labels[key] = lbl_status
            row += 1
        
        # Action Buttons
        btn_frame = tk.Frame(right_frame, bg="#1a1a2a")
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        buttons = [
            ("▶️  START ALL", self.start_all, "#00aa00"),
            ("⏸️  STOP ALL", self.stop_all, "#aa0000"),
            ("🔄  REFRESH", self.refresh, "#0088aa"),
            ("📋 RUN SCAN", self.run_scan, "#8800aa"),
            ("ℹ️  ABOUT", self.show_about, "#555555")
        ]
        
        for text, cmd, color in buttons:
            btn = tk.Button(
                btn_frame,
                text=text,
                command=cmd,
                bg=color,
                fg="#ffffff",
                font=("Consolas", 9, "bold"),
                padx=10,
                pady=5
            )
            btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Log Output
        log_frame = tk.LabelFrame(
            right_frame, 
            text="ACTIVITY LOG", 
            bg="#1a1a2a",
            fg="#00ff00",
            font=("Consolas", 11, "bold"),
            padx=10,
            pady=10
        )
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            bg="#000000",
            fg="#00ff00",
            font=("Consolas", 9),
            insertbackground="#00ff00"
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        self.log("System initialized. Welcome to Deadbolt Sandbox!")
        self.log("This panel shows exactly how all components connect and work.")
        self.log("Click buttons to simulate system behavior!")
        
    def draw_architecture(self, canvas):
        w = 550
        h = 600
        
        # Colors
        color_user = "#00aa00"
        color_kernel = "#aa00aa"
        color_user_text = "#ffffff"
        
        # Title
        canvas.create_text(w//2, 30, text="DEADBOLT SYSTEM ARCHITECTURE", 
                          fill="#00ffff", font=("Consolas", 14, "bold"))
        
        # User Mode Layer
        canvas.create_text(70, 80, text="USER MODE", fill=color_user, font=("Consolas", 12, "bold"))
        
        user_boxes = [
            (100, 100, "retro_ui.py", "Retro UI"),
            (250, 100, "monitor.py", "File Monitor"),
            (400, 100, "threat_mitigation.py", "Threat Mitigation"),
            (100, 200, "ransomware_detector.py", "Ransomware Shield"),
            (250, 200, "zip_bomb_detector.py", "Zip Bomb Detector"),
            (400, 200, "SECURITY_DASHBOARD.py", "Dashboard")
        ]
        
        for x, y, file, label in user_boxes:
            canvas.create_rectangle(x, y, x+120, y+50, fill="#1a3a1a", outline=color_user, width=2)
            canvas.create_text(x+60, y+15, text=file, fill=color_user_text, font=("Consolas", 7))
            canvas.create_text(x+60, y+35, text=label, fill="#00ff00", font=("Consolas", 9))
        
        # Kernel Mode Layer
        canvas.create_text(70, 350, text="KERNEL MODE", fill=color_kernel, font=("Consolas", 12, "bold"))
        
        kernel_boxes = [
            (150, 380, "DeadboltEDR.sys", "EDR Driver"),
            (350, 380, "DeadboltMinifilter.sys", "File Minifilter")
        ]
        
        for x, y, file, label in kernel_boxes:
            canvas.create_rectangle(x, y, x+140, y+60, fill="#3a1a3a", outline=color_kernel, width=2)
            canvas.create_text(x+70, y+20, text=file, fill=color_user_text, font=("Consolas", 7))
            canvas.create_text(x+70, y+45, text=label, fill="#ff88ff", font=("Consolas", 9))
        
        # Arrows
        for i in range(3):
            canvas.create_line(160+i*150, 150, 160+i*150, 380, 
                           arrow=tk.LAST, fill="#888888", width=2, dash=(5,5))
        
        canvas.create_line(220, 150, 220, 380, 
                           arrow=tk.LAST, fill="#888888", width=2, dash=(5,5))
        
        canvas.create_line(310, 150, 310, 380, 
                           arrow=tk.LAST, fill="#888888", width=2, dash=(5,5))
        
        # System Layer
        canvas.create_text(w//2, 520, text="SYSTEM LAYER (Files, Registry, Network)", 
                          fill="#ffff00", font=("Consolas", 11))
        
        canvas.create_rectangle(50, 540, w-50, 590, fill="#2a2a00", outline="#ffff00", width=2)
        
    def log(self, message):
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        
    def start_all(self):
        self.log("Starting all modules...")
        for key in self.modules:
            if "Not Loaded" not in self.modules[key]["status"]:
                self.modules[key]["status"] = "ACTIVE"
                self.modules[key]["color"] = "#00ff00"
                self.status_labels[key].config(text="ACTIVE", fg="#00ff00")
        self.log("✅ All user-mode modules started!")
        
    def stop_all(self):
        self.log("Stopping all modules...")
        for key in self.modules:
            if "Not Loaded" not in self.modules[key]["status"]:
                self.modules[key]["status"] = "Stopped"
                self.modules[key]["color"] = "#ff5555"
                self.status_labels[key].config(text="Stopped", fg="#ff5555")
        self.log("⏹️  All modules stopped!")
        
    def refresh(self):
        self.log("🔄 Refreshing system state...")
        self.log("✅ System state refreshed!")
        
    def run_scan(self):
        self.log("📋 Starting comprehensive system scan...")
        self.log("   - Scanning for suspicious processes...")
        time.sleep(0.3)
        self.log("   - Checking network connections...")
        time.sleep(0.3)
        self.log("   - Analyzing file system...")
        time.sleep(0.3)
        self.log("✅ Scan complete! No threats found!")
        
    def show_about(self):
        about_text = (
            "DEADBOLT SANDBOX & CONTROL CENTER\n"
            "Version 1.0\n\n"
            "This panel shows exactly:\n"
            "- System Architecture Map\n"
            "- Module Status Grid\n"
            "- Activity Log\n"
            "- How all components connect\n\n"
            "Use this to understand the system!\n"
        )
        messagebox.showinfo("About Deadbolt Sandbox", about_text)

def main():
    root = tk.Tk()
    app = DeadboltSandbox(root)
    root.mainloop()

if __name__ == "__main__":
    main()
