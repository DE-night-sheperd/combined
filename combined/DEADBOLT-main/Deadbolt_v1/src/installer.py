import os
import sys
import json
import time
import tkinter as tk
from tkinter import ttk, messagebox
import ctypes
import shutil

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    if not is_admin():
        script = os.path.abspath(sys.argv[0])
        params = ' '.join([script] + sys.argv[1:])
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
        sys.exit()

class DeadboltInstaller:
    def __init__(self, root):
        self.root = root
        self.root.title("Deadbolt Endpoint Shield v1.0 - Setup")
        self.root.geometry("650x500")
        self.root.resizable(False, False)
        
        self.current_step = 0
        self.secret_offset = 1050
        self.steps = ["Welcome", "License", "Config", "Install", "Complete"]
        
        self.setup_ui()
        self.show_step(0)
        
    def setup_ui(self):
        main = tk.Frame(self.root, bg="#ffffff")
        main.pack(fill=tk.BOTH, expand=True)
        
        left = tk.Frame(main, bg="#005a9e", width=180)
        left.pack(side=tk.LEFT, fill=tk.Y)
        left.pack_propagate(False)
        
        tk.Label(
            left,
            text="DEADBOLT\nENDPOINT\nSHIELD",
            font=("Arial", 14, "bold"),
            fg="#ffffff",
            bg="#005a9e"
        ).pack(pady=40)
        
        self.step_labels = []
        for i, step in enumerate(self.steps):
            lbl = tk.Label(left, text=step, font=("Arial", 9), fg="#a0d0f0", bg="#005a9e", anchor=tk.W)
            lbl.pack(padx=15, pady=5, fill=tk.X)
            self.step_labels.append(lbl)
        
        self.content = tk.Frame(main, bg="#ffffff")
        self.content.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        btn_frame = tk.Frame(main, bg="#f0f0f0", height=60)
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X)
        btn_frame.pack_propagate(False)
        
        self.btn_cancel = tk.Button(btn_frame, text="Cancel", width=10, command=self.on_cancel)
        self.btn_cancel.pack(side=tk.RIGHT, padx=15, pady=15)
        
        self.btn_next = tk.Button(btn_frame, text="Next >", width=10, command=self.on_next, bg="#005a9e", fg="white")
        self.btn_next.pack(side=tk.RIGHT, padx=5, pady=15)
        
        self.btn_back = tk.Button(btn_frame, text="< Back", width=10, command=self.on_back, state=tk.DISABLED)
        self.btn_back.pack(side=tk.RIGHT, padx=5, pady=15)
        
    def clear_content(self):
        for w in self.content.winfo_children():
            w.destroy()
            
    def show_step(self, idx):
        self.current_step = idx
        for i, lbl in enumerate(self.step_labels):
            if i < idx:
                lbl.config(fg="#ffffff")
            elif i == idx:
                lbl.config(fg="#ffffff", font=("Arial", 9, "bold"))
            else:
                lbl.config(fg="#a0d0f0")
        
        self.clear_content()
        if idx == 0:
            self.welcome()
        elif idx == 1:
            self.license()
        elif idx == 2:
            self.config()
        elif idx == 3:
            self.install()
        elif idx == 4:
            self.complete()
            
    def welcome(self):
        tk.Label(
            self.content,
            text="Welcome to Deadbolt Endpoint Shield Setup",
            font=("Arial", 14, "bold"),
            bg="#ffffff"
        ).pack(pady=(40,20), padx=30, anchor=tk.W)
        
        tk.Label(
            self.content,
            text="This wizard will install Deadbolt Endpoint Shield v1.0 on your computer.",
            font=("Arial", 10),
            bg="#ffffff",
            wraplength=400,
            justify=tk.LEFT
        ).pack(pady=10, padx=30, anchor=tk.W)
        
        tk.Label(
            self.content,
            text="Click Next to continue.",
            font=("Arial", 10),
            bg="#ffffff"
        ).pack(pady=20, padx=30, anchor=tk.W)
        
        self.btn_back.config(state=tk.DISABLED)
        self.btn_next.config(text="Next >", state=tk.NORMAL)
        
    def license(self):
        tk.Label(
            self.content,
            text="POPIA License Agreement",
            font=("Arial", 14, "bold"),
            bg="#ffffff"
        ).pack(pady=(30,15), padx=30, anchor=tk.W)
        
        txt = """This software collects and processes personal information for security monitoring purposes only.

By clicking "I Agree" and continuing, you consent to the collection and processing of this information in accordance with the Protection of Personal Information Act (POPIA) of South Africa.

All data is stored locally and is not transmitted to external servers."""
        
        text_box = tk.Text(self.content, height=12, wrap=tk.WORD, font=("Arial", 9), bg="#f8f8f8", padx=10, pady=10)
        text_box.insert(tk.END, txt)
        text_box.config(state=tk.DISABLED)
        text_box.pack(padx=30, pady=10, fill=tk.BOTH, expand=True)
        
        self.agree_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            self.content,
            text="I accept the agreement",
            variable=self.agree_var,
            bg="#ffffff",
            font=("Arial", 10),
            command=lambda: self.btn_next.config(state=tk.NORMAL if self.agree_var.get() else tk.DISABLED)
        ).pack(pady=15, padx=30, anchor=tk.W)
        
        self.btn_back.config(state=tk.NORMAL)
        self.btn_next.config(text="Next >", state=tk.DISABLED)
        
    def config(self):
        tk.Label(
            self.content,
            text="Configuration",
            font=("Arial", 14, "bold"),
            bg="#ffffff"
        ).pack(pady=(30,15), padx=30, anchor=tk.W)
        
        tk.Label(
            self.content,
            text="Enter the secret key offset for unlock verification.",
            font=("Arial", 10),
            bg="#ffffff"
        ).pack(pady=10, padx=30, anchor=tk.W)
        
        frame = tk.Frame(self.content, bg="#ffffff")
        frame.pack(pady=20, padx=30, anchor=tk.W)
        
        tk.Label(frame, text="Secret Key Offset:", font=("Arial", 10, "bold"), bg="#ffffff").pack(side=tk.LEFT)
        self.entry = tk.Entry(frame, font=("Arial", 12), width=15, justify=tk.CENTER)
        self.entry.insert(0, "1050")
        self.entry.pack(side=tk.LEFT, padx=10)
        
        self.btn_back.config(state=tk.NORMAL)
        self.btn_next.config(text="Install", state=tk.NORMAL)
        
    def install(self):
        tk.Label(
            self.content,
            text="Installing...",
            font=("Arial", 14, "bold"),
            bg="#ffffff"
        ).pack(pady=(50,30), padx=30, anchor=tk.W)
        
        self.progress = ttk.Progressbar(self.content, orient=tk.HORIZONTAL, length=380, mode='determinate')
        self.progress.pack(pady=20, padx=30)
        
        self.lbl = tk.Label(self.content, text="Initializing...", font=("Arial", 10), bg="#ffffff")
        self.lbl.pack(pady=10, padx=30, anchor=tk.W)
        
        self.btn_back.config(state=tk.DISABLED)
        self.btn_next.config(state=tk.DISABLED)
        self.btn_cancel.config(state=tk.DISABLED)
        
        self.root.after(100, self.do_install)
        
    def do_install(self):
        steps = ["Creating directories...", "Saving config...", "Copying files...", "Finalizing..."]
        for i, s in enumerate(steps):
            self.lbl.config(text=s)
            self.progress['value'] = (i+1)/len(steps)*100
            self.root.update()
            time.sleep(0.6)
            
        try:
            self.secret_offset = int(self.entry.get())
            appdata = os.path.join(os.environ["ProgramData"], "Deadbolt_v1")
            os.makedirs(appdata, exist_ok=True)
            config = {"SecretKeyOffset": self.secret_offset, "InstallDate": time.strftime("%Y-%m-%dT%H:%M:%SZ"), "Version": "1.0"}
            with open(os.path.join(appdata, "config.json"), "w") as f:
                json.dump(config, f, indent=4)
                
            src_dir = os.path.dirname(os.path.abspath(__file__))
            for f in ["daemon.py", "monitor.py", "simulator.py"]:
                shutil.copy2(os.path.join(src_dir, f), appdata)
        except Exception as e:
            messagebox.showerror("Error", f"Failed: {str(e)}")
            self.on_cancel()
            return
            
        self.root.after(500, lambda: self.show_step(4))
        
    def complete(self):
        tk.Label(
            self.content,
            text="Setup Complete!",
            font=("Arial", 14, "bold"),
            bg="#ffffff"
        ).pack(pady=(40,20), padx=30, anchor=tk.W)
        
        tk.Label(
            self.content,
            text="Deadbolt Endpoint Shield has been installed successfully.",
            font=("Arial", 10),
            bg="#ffffff"
        ).pack(pady=10, padx=30, anchor=tk.W)
        
        self.launch = tk.BooleanVar(value=True)
        tk.Checkbutton(
            self.content,
            text="Launch Deadbolt now",
            variable=self.launch,
            bg="#ffffff",
            font=("Arial", 10)
        ).pack(pady=30, padx=30, anchor=tk.W)
        
        self.btn_back.config(state=tk.DISABLED)
        self.btn_next.config(text="Finish", state=tk.NORMAL, command=self.on_finish)
        self.btn_cancel.config(state=tk.DISABLED)
        
    def on_next(self):
        if self.current_step < len(self.steps)-1:
            self.show_step(self.current_step+1)
            
    def on_back(self):
        if self.current_step > 0:
            self.show_step(self.current_step-1)
            
    def on_cancel(self):
        if messagebox.askyesno("Cancel", "Are you sure?"):
            self.root.destroy()
            
    def on_finish(self):
        self.root.destroy()
        if self.launch.get():
            self.launch_deadbolt()
            
    def launch_deadbolt(self):
        daemon = os.path.join(os.path.dirname(os.path.abspath(__file__)), "daemon.py")
        if os.path.exists(daemon):
            os.chdir(os.path.dirname(daemon))
            import subprocess
            subprocess.Popen([sys.executable, daemon])

def main():
    run_as_admin()
    root = tk.Tk()
    app = DeadboltInstaller(root)
    root.mainloop()

if __name__ == "__main__":
    main()
