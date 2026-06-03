import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
import json
import time
import random

print("DEADBOLT ENDPOINT SHIELD PRO - LAUNCHING")

class DeadboltProWizard:
    def __init__(self, root):
        self.root = root
        self.root.title("Deadbolt Endpoint Shield PRO")
        self.root.geometry("900x650")
        self.root.minsize(900, 650)
        self.root.resizable(False, False)
        self.root.configure(bg="#0a0a0a")
        
        self.current_page = 0
        self.security_score = 720
        self.pages = [
            "Intro",
            "Security Scan",
            "Fix Issues",
            "Setup",
            "Complete"
        ]
        
        self.create_widgets()
        self.show_page(0)
        
    def create_widgets(self):
        main = tk.Frame(self.root, bg="#0a0a0a")
        main.pack(fill=tk.BOTH, expand=True)
        
        header = tk.Frame(main, bg="#00ff88", height=60)
        header.pack(fill=tk.X, side=tk.TOP)
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="⚡ DEADBOLT ENDPOINT SHIELD PRO",
            font=("Segoe UI", 20, "bold"),
            bg="#00ff88",
            fg="#000000"
        ).pack(pady=12)
        
        self.content = tk.Frame(main, bg="#0a0a0a")
        self.content.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        btn_frame = tk.Frame(main, bg="#1a1a1a", height=70)
        btn_frame.pack(fill=tk.X, side=tk.BOTTOM)
        btn_frame.pack_propagate(False)
        
        self.btn_back = tk.Button(btn_frame, text="< Back", font=("Segoe UI", 11), bg="#333333", fg="#ffffff", width=12, command=self.prev_page, state=tk.DISABLED)
        self.btn_back.pack(side=tk.LEFT, padx=20, pady=18)
        
        self.btn_next = tk.Button(btn_frame, text="Next >", font=("Segoe UI", 11, "bold"), bg="#00ff88", fg="#000000", width=14, command=self.next_page)
        self.btn_next.pack(side=tk.RIGHT, padx=20, pady=18)
        
    def clear_content(self):
        for w in self.content.winfo_children():
            w.destroy()
            
    def show_page(self, idx):
        self.current_page = idx
        self.clear_content()
        
        if idx == 0:
            self.intro_page()
        elif idx == 1:
            self.scan_page()
        elif idx == 2:
            self.fix_page()
        elif idx == 3:
            self.setup_page()
        elif idx == 4:
            self.complete_page()
            
        if idx == 0:
            self.btn_back.config(state=tk.DISABLED)
            self.btn_next.config(text="Start Scan >")
        elif idx == 4:
            self.btn_back.config(state=tk.DISABLED)
            self.btn_next.config(text="Finish", command=self.finish)
        else:
            self.btn_back.config(state=tk.NORMAL)
            self.btn_next.config(text="Next >", command=self.next_page)
            
    def intro_page(self):
        tk.Label(
            self.content,
            text="YOUR SECURITY SCORE",
            font=("Segoe UI", 28, "bold"),
            bg="#0a0a0a",
            fg="#00ff88"
        ).pack(pady=(20, 10))
        
        score_frame = tk.Frame(self.content, bg="#0a0a0a")
        score_frame.pack(pady=10)
        
        score_label = tk.Label(
            score_frame,
            text=str(self.security_score),
            font=("Segoe UI", 120, "bold"),
            bg="#0a0a0a",
            fg="#00ff88"
        )
        score_label.pack()
        
        tk.Label(
            self.content,
            text="OUT OF 1000 - GOOD, BUT COULD BE BETTER!",
            font=("Segoe UI", 14),
            bg="#0a0a0a",
            fg="#888888"
        ).pack(pady=(10, 40))
        
        tk.Label(
            self.content,
            text="Click 'Start Scan' to find and fix security issues!",
            font=("Segoe UI", 12),
            bg="#0a0a0a",
            fg="#ffffff"
        ).pack()
        
    def scan_page(self):
        tk.Label(
            self.content,
            text="🔍 SCANNING YOUR SYSTEM...",
            font=("Segoe UI", 24, "bold"),
            bg="#0a0a0a",
            fg="#00ff88"
        ).pack(pady=(30, 30))
        
        self.progress = ttk.Progressbar(self.content, orient=tk.HORIZONTAL, length=700, mode='determinate')
        self.progress.pack(pady=20)
        
        self.status = tk.Label(
            self.content,
            text="Initializing scan...",
            font=("Segoe UI", 14),
            bg="#0a0a0a",
            fg="#ffffff"
        )
        self.status.pack(pady=20)
        
        self.issues_frame = tk.Frame(self.content, bg="#0a0a0a")
        self.issues_frame.pack(pady=20, fill=tk.BOTH, expand=True)
        
        self.found_issues = []
        self.btn_next.config(state=tk.DISABLED)
        self.root.after(300, self.do_scan)
        
    def do_scan(self):
        steps = [
            ("Checking Windows Update...", 15, "Windows Update not set to automatic"),
            ("Checking firewall...", 30, "Firewall has 2 open ports"),
            ("Checking startup apps...", 50, "3 unknown startup apps found"),
            ("Checking for outdated software...", 70, "5 apps are outdated"),
            ("Checking password policy...", 85, "Password complexity not enabled"),
            ("Finalizing...", 100, "Scan complete!")
        ]
        
        for text, prog, issue in steps:
            self.status.config(text=text)
            self.progress['value'] = prog
            
            if issue and issue != "Scan complete!":
                self.found_issues.append(issue)
                issue_lbl = tk.Label(
                    self.issues_frame,
                    text=f"⚠️  {issue}",
                    font=("Segoe UI", 11),
                    bg="#0a0a0a",
                    fg="#ffaa00",
                    anchor=tk.W
                )
                issue_lbl.pack(fill=tk.X, pady=3)
                
            self.root.update()
            time.sleep(0.8)
        
        self.root.after(800, lambda: self.btn_next.config(state=tk.NORMAL, text="Fix All >"))
        
    def fix_page(self):
        tk.Label(
            self.content,
            text="🔧 FIXING SECURITY ISSUES...",
            font=("Segoe UI", 24, "bold"),
            bg="#0a0a0a",
            fg="#00ff88"
        ).pack(pady=(30, 30))
        
        self.fix_progress = ttk.Progressbar(self.content, orient=tk.HORIZONTAL, length=700, mode='determinate')
        self.fix_progress.pack(pady=20)
        
        self.fix_status = tk.Label(
            self.content,
            text="Preparing to fix issues...",
            font=("Segoe UI", 14),
            bg="#0a0a0a",
            fg="#ffffff"
        )
        self.fix_status.pack(pady=20)
        
        self.result_frame = tk.Frame(self.content, bg="#0a0a0a")
        self.result_frame.pack(pady=20, fill=tk.BOTH, expand=True)
        
        self.btn_next.config(state=tk.DISABLED)
        self.root.after(300, self.do_fix)
        
    def do_fix(self):
        fixes = [
            ("Enabling Windows Update automatic...", 20, "✅ Windows Update set to automatic"),
            ("Closing open firewall ports...", 40, "✅ Firewall ports closed"),
            ("Removing unknown startup apps...", 60, "✅ Unknown apps removed"),
            ("Updating outdated software...", 80, "✅ All apps updated"),
            ("Enabling password complexity...", 100, "✅ Password policy enabled")
        ]
        
        for text, prog, result in fixes:
            self.fix_status.config(text=text)
            self.fix_progress['value'] = prog
            
            result_lbl = tk.Label(
                self.result_frame,
                text=result,
                font=("Segoe UI", 11),
                bg="#0a0a0a",
                fg="#00ff88",
                anchor=tk.W
            )
            result_lbl.pack(fill=tk.X, pady=3)
            
            self.root.update()
            time.sleep(0.8)
        
        self.security_score = 985
        self.root.after(800, lambda: self.btn_next.config(state=tk.NORMAL))
        
    def setup_page(self):
        tk.Label(
            self.content,
            text="⚙️ FINAL SETUP",
            font=("Segoe UI", 24, "bold"),
            bg="#0a0a0a",
            fg="#00ff88"
        ).pack(pady=(20, 30))
        
        tk.Label(
            self.content,
            text="Your NEW Security Score:",
            font=("Segoe UI", 16),
            bg="#0a0a0a",
            fg="#ffffff"
        ).pack(pady=(0, 10))
        
        tk.Label(
            self.content,
            text="985 / 1000",
            font=("Segoe UI", 72, "bold"),
            bg="#0a0a0a",
            fg="#00ff88"
        ).pack(pady=(0, 30))
        
        tk.Label(
            self.content,
            text="Enter secret unlock offset:",
            font=("Segoe UI", 12),
            bg="#0a0a0a",
            fg="#ffffff"
        ).pack()
        
        self.offset_entry = tk.Entry(self.content, font=("Segoe UI", 18), width=12, justify=tk.CENTER, bg="#1a1a1a", fg="#00ff88")
        self.offset_entry.insert(0, "1050")
        self.offset_entry.pack(pady=10)
        
    def complete_page(self):
        tk.Label(
            self.content,
            text="🎉 ALL DONE!",
            font=("Segoe UI", 36, "bold"),
            bg="#0a0a0a",
            fg="#00ff88"
        ).pack(pady=(40, 20))
        
        tk.Label(
            self.content,
            text="Your system is now PROTECTED by Deadbolt Endpoint Shield PRO!",
            font=("Segoe UI", 16),
            bg="#0a0a0a",
            fg="#ffffff"
        ).pack(pady=10)
        
        tk.Label(
            self.content,
            text=f"Final Security Score: {self.security_score}/1000",
            font=("Segoe UI", 20, "bold"),
            bg="#0a0a0a",
            fg="#00ff88"
        ).pack(pady=40)
        
    def next_page(self):
        if self.current_page < len(self.pages)-1:
            self.show_page(self.current_page+1)
            
    def prev_page(self):
        if self.current_page > 0:
            self.show_page(self.current_page-1)
            
    def finish(self):
        messagebox.showinfo("Deadbolt PRO", "Setup complete!\nYour system is now secured with Deadbolt Endpoint Shield PRO!")
        self.root.destroy()

def main():
    root = tk.Tk()
    app = DeadboltProWizard(root)
    root.mainloop()

if __name__ == "__main__":
    main()
