import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
import json
import win32serviceutil
import win32service
import win32event
import servicemanager
import threading
import time

print("DEADBOLT ENDPOINT SHIELD - SERVICE MANAGER")

class DeadboltBackgroundService(win32serviceutil.ServiceFramework):
    _svc_name_ = "DeadboltEndpointShield"
    _svc_display_name_ = "Deadbolt Endpoint Shield Service"
    _svc_description_ = "Provides real-time endpoint protection and security monitoring"
    
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.is_alive = True
        
    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.is_alive = False
        win32event.SetEvent(self.hWaitStop)
        
    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))
        self.main()
        
    def main(self):
        appdata = os.path.join(os.environ["ProgramData"], "DeadboltEndpointShield")
        config_path = os.path.join(appdata, "config.json")
        
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                config = json.load(f)
        else:
            config = {"SecretKeyOffset": 1050}
            
        while self.is_alive:
            time.sleep(5)

class ServiceManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Deadbolt Endpoint Shield - Service Manager")
        self.root.geometry("700x500")
        self.root.resizable(False, False)
        self.root.configure(bg="#0a0a0a")
        
        self.create_widgets()
        
    def create_widgets(self):
        header = tk.Frame(self.root, bg="#00ff88", height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="⚙️ DEADBOLT SERVICE MANAGER",
            font=("Segoe UI", 18, "bold"),
            bg="#00ff88",
            fg="#000000"
        ).pack(pady=15)
        
        content = tk.Frame(self.root, bg="#0a0a0a")
        content.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        tk.Label(
            content,
            text="Background Service & Boot Options",
            font=("Segoe UI", 20, "bold"),
            bg="#0a0a0a",
            fg="#00ff88"
        ).pack(pady=(0, 30), anchor=tk.W)
        
        options_frame = tk.LabelFrame(content, text="Service Options", bg="#0a0a0a", fg="#00ff88", font=("Segoe UI", 12, "bold"), padx=20, pady=20)
        options_frame.pack(fill=tk.X, pady=10)
        
        self.startup_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            options_frame,
            text="Start Deadbolt automatically when Windows boots",
            variable=self.startup_var,
            bg="#0a0a0a",
            fg="#ffffff",
            font=("Segoe UI", 11),
            selectcolor="#0a0a0a",
            activebackground="#0a0a0a",
            activeforeground="#00ff88"
        ).pack(anchor=tk.W, pady=8)
        
        self.boot_scan_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            options_frame,
            text="Run quick boot-time scan right after Windows logo",
            variable=self.boot_scan_var,
            bg="#0a0a0a",
            fg="#ffffff",
            font=("Segoe UI", 11),
            selectcolor="#0a0a0a",
            activebackground="#0a0a0a",
            activeforeground="#00ff88"
        ).pack(anchor=tk.W, pady=8)
        
        self.background_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            options_frame,
            text="Run in background for real-time protection",
            variable=self.background_var,
            bg="#0a0a0a",
            fg="#ffffff",
            font=("Segoe UI", 11),
            selectcolor="#0a0a0a",
            activebackground="#0a0a0a",
            activeforeground="#00ff88"
        ).pack(anchor=tk.W, pady=8)
        
        btn_frame = tk.Frame(content, bg="#0a0a0a")
        btn_frame.pack(fill=tk.X, pady=30)
        
        tk.Button(
            btn_frame,
            text="Apply Settings",
            font=("Segoe UI", 12, "bold"),
            bg="#00ff88",
            fg="#000000",
            width=18,
            command=self.apply_settings
        ).pack(side=tk.RIGHT, padx=5)
        
        tk.Button(
            btn_frame,
            text="Start Service Now",
            font=("Segoe UI", 12),
            bg="#333333",
            fg="#ffffff",
            width=18,
            command=self.start_service
        ).pack(side=tk.RIGHT, padx=5)
        
    def apply_settings(self):
        appdata = os.path.join(os.environ["ProgramData"], "DeadboltEndpointShield")
        os.makedirs(appdata, exist_ok=True)
        
        config = {
            "StartOnBoot": self.startup_var.get(),
            "BootScan": self.boot_scan_var.get(),
            "RunInBackground": self.background_var.get(),
            "LastConfigured": time.strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        
        config_path = os.path.join(appdata, "service_config.json")
        with open(config_path, "w") as f:
            json.dump(config, f, indent=4)
            
        messagebox.showinfo("Success", "Settings applied successfully!")
        
    def start_service(self):
        messagebox.showinfo("Service", "Deadbolt background service would start now!\n(In production, this would install and start the Windows service)")

def main():
    if len(sys.argv) == 1:
        root = tk.Tk()
        app = ServiceManagerApp(root)
        root.mainloop()
    else:
        win32serviceutil.HandleCommandLine(DeadboltBackgroundService)

if __name__ == "__main__":
    main()
