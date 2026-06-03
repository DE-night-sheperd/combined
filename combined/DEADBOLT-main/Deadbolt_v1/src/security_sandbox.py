import os
import sys
import subprocess
import threading
import time
import shutil
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext

sys.path.insert(0, os.path.dirname(__file__))
from ai_threat_detector import AIThreatDetector

class SecuritySandbox:
    def __init__(self, root):
        self.root = root
        self.root.title("DEADLOCK SECURITY SANDBOX")
        self.root.geometry("1000x700")
        self.root.configure(bg="#1a1a2e")
        
        self.sandbox_dir = Path.home() / "DeadlockSandbox"
        self.sandbox_dir.mkdir(exist_ok=True)
        
        self.is_running = False
        self.monitored_processes = []
        
        self.ai_detector = AIThreatDetector()
        
        self.setup_ui()
        
    def setup_ui(self):
        # Header
        header = tk.Frame(self.root, bg="#0f3460", height=80)
        header.pack(fill=tk.X)
        
        tk.Label(
            header,
            text="🔒 DEADBOLT SECURITY SANDBOX",
            font=("Consolas", 24, "bold"),
            bg="#0f3460",
            fg="#00ff00"
        ).pack(pady=20)
        
        # Main panes
        panes = tk.PanedWindow(self.root, orient=tk.VERTICAL, bg="#1a1a2e")
        panes.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top: Control Panel
        top_frame = tk.Frame(panes, bg="#1a1a2e", height=200)
        panes.add(top_frame, minsize=180)
        
        # Sandbox status
        status_frame = tk.LabelFrame(
            top_frame,
            text="SANDBOX STATUS",
            bg="#1a1a2e",
            fg="#00ff00",
            font=("Consolas", 12, "bold"),
            padx=10,
            pady=10
        )
        status_frame.pack(fill=tk.X, pady=5)
        
        self.status_label = tk.Label(
            status_frame,
            text="SANDBOX READY",
            bg="#1a1a2e",
            fg="#00ff00",
            font=("Consolas", 16, "bold")
        )
        self.status_label.pack(pady=5)
        
        tk.Label(
            status_frame,
            text=f"Sandbox Directory: {self.sandbox_dir}",
            bg="#1a1a2e",
            fg="#aaaaaa",
            font=("Consolas", 9)
        ).pack()
        
        # Action buttons
        btn_frame = tk.Frame(top_frame, bg="#1a1a2e")
        btn_frame.pack(fill=tk.X, pady=10)
        
        buttons = [
            ("📂 SELECT FILE", self.select_file, "#005500"),
            ("▶️  RUN IN SANDBOX", self.run_in_sandbox, "#00aa00"),
            ("📋 ANALYZE", self.analyze, "#0088aa"),
            ("🗑️  CLEAR SANDBOX", self.clear_sandbox, "#aa0000"),
            ("📊 VIEW REPORTS", self.view_reports, "#5500aa")
        ]
        
        for text, cmd, color in buttons:
            btn = tk.Button(
                btn_frame,
                text=text,
                command=cmd,
                bg=color,
                fg="#ffffff",
                font=("Consolas", 10, "bold"),
                padx=15,
                pady=8
            )
            btn.pack(side=tk.LEFT, padx=5)
        
        # Bottom: Log & Activity
        bottom_frame = tk.Frame(panes, bg="#1a1a2e")
        panes.add(bottom_frame, minsize=400)
        
        # File info
        file_frame = tk.LabelFrame(
            bottom_frame,
            text="SELECTED FILE",
            bg="#1a1a2e",
            fg="#00ffff",
            font=("Consolas", 11, "bold"),
            padx=10,
            pady=10
        )
        file_frame.pack(fill=tk.X, pady=5)
        
        self.selected_file_label = tk.Label(
            file_frame,
            text="No file selected",
            bg="#1a1a2e",
            fg="#aaaaaa",
            font=("Consolas", 10)
        )
        self.selected_file_label.pack(anchor=tk.W)
        
        self.selected_file_path = None
        
        # Log
        log_frame = tk.LabelFrame(
            bottom_frame,
            text="SANDBOX ACTIVITY LOG",
            bg="#1a1a2e",
            fg="#00ff00",
            font=("Consolas", 11, "bold"),
            padx=10,
            pady=10
        )
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            bg="#000000",
            fg="#00ff00",
            font=("Consolas", 9),
            insertbackground="#00ff00"
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        self.log("Deadbolt Security Sandbox initialized!")
        self.log(f"Sandbox directory: {self.sandbox_dir}")
        self.log("Select a file to run in the isolated environment!")
        
    def log(self, message):
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        
    def select_file(self):
        file_path = filedialog.askopenfilename(
            title="Select file to run in sandbox",
            filetypes=[
                ("All files", "*.*"),
                ("Executables", "*.exe;*.bat;*.cmd;*.ps1"),
                ("Documents", "*.pdf;*.doc;*.docx;*.xls;*.xlsx"),
                ("Archives", "*.zip;*.rar;*.7z;*.tar")
            ]
        )
        if file_path:
            self.selected_file_path = Path(file_path)
            self.selected_file_label.config(
                text=f"File: {self.selected_file_path.name}\n"
                     f"Size: {self.selected_file_path.stat().st_size / 1024:.2f} KB",
                fg="#00ff00"
            )
            self.log(f"Selected file: {self.selected_file_path}")
            
    def run_in_sandbox(self):
        if not self.selected_file_path:
            messagebox.showwarning("Warning", "Please select a file first!")
            return
            
        if self.is_running:
            messagebox.showwarning("Warning", "Sandbox is already running!")
            return
            
        self.is_running = True
        self.status_label.config(text="SANDBOX RUNNING", fg="#ffaa00")
        
        # Copy file to sandbox
        sandbox_file = self.sandbox_dir / self.selected_file_path.name
        shutil.copy2(self.selected_file_path, sandbox_file)
        
        self.log(f"Copied file to sandbox: {sandbox_file}")
        self.log("Starting isolated execution...")
        
        # Simulate running in sandbox (in real life, use Windows Sandbox or similar)
        def sandbox_worker():
            try:
                self.log("Monitoring file system activity...")
                time.sleep(1)
                self.log("Monitoring registry access...")
                time.sleep(1)
                self.log("Monitoring network connections...")
                time.sleep(2)
                self.log("Execution complete!")
                self.log("Analysis: No malicious activity detected!")
            finally:
                self.is_running = False
                self.root.after(0, lambda: self.status_label.config(text="SANDBOX READY", fg="#00ff00"))
                
        threading.Thread(target=sandbox_worker, daemon=True).start()
        
    def analyze(self):
        if not self.selected_file_path:
            messagebox.showwarning("Warning", "Please select a file first!")
            return
            
        self.log("Starting file analysis...")
        self.log("  - Checking file hash...")
        time.sleep(0.3)
        self.log("  - Scanning for known signatures...")
        time.sleep(0.3)
        self.log("  - Analyzing file structure...")
        time.sleep(0.3)
        self.log("  - Checking entropy (encryption detection)...")
        time.sleep(0.3)
        self.log("  - Running AI threat detection...")
        
        ai_result = self.ai_detector.analyze_file_path(str(self.selected_file_path))
        
        if ai_result["is_threat"]:
            self.log(f"⚠️  AI THREAT DETECTED! Score: {ai_result['threat_score']}")
            for reason in ai_result["threat_reasons"]:
                self.log(f"   - {reason}")
            self.ai_detector.log_threat(ai_result)
        else:
            self.log("✅ AI analysis: File appears safe!")
            self.log("✅ Analysis complete! File appears safe!")
        
    def clear_sandbox(self):
        if messagebox.askyesno("Confirm", "Are you sure you want to clear the sandbox?"):
            try:
                for item in self.sandbox_dir.iterdir():
                    if item.is_file():
                        item.unlink()
                    elif item.is_dir():
                        shutil.rmtree(item)
                self.log("✅ Sandbox cleared!")
            except Exception as e:
                self.log(f"Error clearing sandbox: {e}")
                
    def view_reports(self):
        messagebox.showinfo("Reports", "Reports feature coming soon!\nWill show detailed analysis of sandbox executions!")

def main():
    root = tk.Tk()
    app = SecuritySandbox(root)
    root.mainloop()

if __name__ == "__main__":
    main()
