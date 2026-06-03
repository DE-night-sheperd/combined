import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk  # Note: If missing, install with: pip install pillow
import os
import sys
import json
import time
import shutil

print("=== DEADBOLT ENDPOINT SHIELD - PROFESSIONAL SETUP WIZARD ===")

class ModernInstallerWizard:
    def __init__(self, root):
        self.root = root
        self.root.title("Deadbolt Endpoint Shield v1.0 Setup")
        self.root.geometry("800x600")
        self.root.minsize(800, 600)
        self.root.resizable(False, False)
        
        self.current_page = 0
        self.secret_offset = 1050
        self.install_path = os.path.join(os.environ["ProgramFiles"], "DeadboltEndpointShield")
        self.pages = [
            "Welcome",
            "License Agreement",
            "Installation Folder",
            "Configuration",
            "Ready to Install",
            "Installing",
            "Completing"
        ]
        
        self.setup_styles()
        self.create_widgets()
        self.show_page(0)
        
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('Wizard.TFrame', background='#ffffff')
        style.configure('Wizard.TLabel', background='#ffffff', font=('Segoe UI', 9))
        style.configure('Title.TLabel', background='#ffffff', font=('Segoe UI', 14, 'bold'))
        style.configure('Subtitle.TLabel', background='#ffffff', font=('Segoe UI', 11))
        style.configure('Wizard.TButton', font=('Segoe UI', 9), padding=5)
        style.configure('Sidebar.TFrame', background='#0078d7')
        style.configure('Sidebar.TLabel', background='#0078d7', foreground='#ffffff', font=('Segoe UI', 9))
        style.configure('SidebarTitle.TLabel', background='#0078d7', foreground='#ffffff', font=('Segoe UI', 16, 'bold'))
        
    def create_widgets(self):
        main_container = ttk.Frame(self.root, style='Wizard.TFrame')
        main_container.pack(fill=tk.BOTH, expand=True)
        
        sidebar = ttk.Frame(main_container, style='Sidebar.TFrame', width=200)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)
        
        ttk.Label(
            sidebar,
            text="DEADBOLT\nENDPOINT\nSHIELD",
            style='SidebarTitle.TLabel'
        ).pack(pady=(30, 20))
        
        self.page_indicators = []
        for i, page in enumerate(self.pages):
            lbl = ttk.Label(
                sidebar,
                text=f"{i+1}. {page}",
                style='Sidebar.TLabel',
                anchor=tk.W
            )
            lbl.pack(padx=15, pady=4, fill=tk.X)
            self.page_indicators.append(lbl)
        
        content_area = ttk.Frame(main_container, style='Wizard.TFrame')
        content_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.content_frame = ttk.Frame(content_area, style='Wizard.TFrame')
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        button_container = ttk.Frame(content_area, style='Wizard.TFrame')
        button_container.pack(fill=tk.X, side=tk.BOTTOM, pady=15)
        
        ttk.Separator(button_container, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=(0, 10))
        
        btn_frame = ttk.Frame(button_container, style='Wizard.TFrame')
        btn_frame.pack(fill=tk.X)
        
        self.btn_cancel = ttk.Button(btn_frame, text="Cancel", style='Wizard.TButton', command=self.cancel)
        self.btn_cancel.pack(side=tk.RIGHT, padx=(0, 15))
        
        self.btn_next = ttk.Button(btn_frame, text="Next >", style='Wizard.TButton', command=self.next_page)
        self.btn_next.pack(side=tk.RIGHT, padx=5)
        
        self.btn_back = ttk.Button(btn_frame, text="< Back", style='Wizard.TButton', command=self.prev_page, state=tk.DISABLED)
        self.btn_back.pack(side=tk.RIGHT, padx=5)
        
    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
    def update_page_indicators(self):
        for i, lbl in enumerate(self.page_indicators):
            if i < self.current_page:
                lbl.configure(foreground='#a0d0f0', font=('Segoe UI', 9))
            elif i == self.current_page:
                lbl.configure(foreground='#ffffff', font=('Segoe UI', 9, 'bold'))
            else:
                lbl.configure(foreground='#60a0d0', font=('Segoe UI', 9))
                
    def show_page(self, index):
        self.current_page = index
        self.update_page_indicators()
        self.clear_content()
        
        if index == 0:
            self.welcome_page()
        elif index == 1:
            self.license_page()
        elif index == 2:
            self.folder_page()
        elif index == 3:
            self.config_page()
        elif index == 4:
            self.ready_page()
        elif index == 5:
            self.install_page()
        elif index == 6:
            self.complete_page()
            
    def welcome_page(self):
        ttk.Label(
            self.content_frame,
            text="Welcome to the Deadbolt Endpoint Shield Setup Wizard",
            style='Title.TLabel'
        ).pack(anchor=tk.W, pady=(0, 20))
        
        ttk.Label(
            self.content_frame,
            text="This wizard will guide you through the installation of Deadbolt Endpoint Shield v1.0.",
            style='Subtitle.TLabel'
        ).pack(anchor=tk.W, pady=(0, 30))
        
        info_frame = ttk.Frame(self.content_frame, style='Wizard.TFrame')
        info_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(
            info_frame,
            text="It is recommended that you close all other applications before starting Setup.",
            style='Wizard.TLabel'
        ).pack(anchor=tk.W, pady=5)
        
        ttk.Label(
            info_frame,
            text="Click Next to continue, or Cancel to exit Setup.",
            style='Wizard.TLabel'
        ).pack(anchor=tk.W, pady=5)
        
        self.btn_back.config(state=tk.DISABLED)
        self.btn_next.config(text="Next >", state=tk.NORMAL)
        
    def license_page(self):
        ttk.Label(
            self.content_frame,
            text="License Agreement",
            style='Title.TLabel'
        ).pack(anchor=tk.W, pady=(0, 15))
        
        ttk.Label(
            self.content_frame,
            text="Please read the following license agreement carefully.",
            style='Subtitle.TLabel'
        ).pack(anchor=tk.W, pady=(0, 15))
        
        license_text = """PROTECTION OF PERSONAL INFORMATION ACT (POPIA) AGREEMENT

This software collects and processes personal information for security monitoring purposes only.

By clicking "I accept the terms in the License Agreement" and continuing with the installation, you consent to the collection and processing of this information in accordance with the Protection of Personal Information Act (POPIA) of South Africa.

All data is stored locally on this device and is not transmitted to any external servers.

Deadbolt Endpoint Shield v1.0
Copyright (c) 2026"""
        
        text_frame = ttk.Frame(self.content_frame, style='Wizard.TFrame')
        text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        license_box = tk.Text(text_frame, wrap=tk.WORD, font=('Segoe UI', 9), bg='#f8f8f8', bd=1, relief=tk.SOLID)
        license_box.insert(tk.END, license_text)
        license_box.config(state=tk.DISABLED)
        
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=license_box.yview)
        license_box.configure(yscrollcommand=scrollbar.set)
        
        license_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.accept_var = tk.BooleanVar(value=False)
        
        def toggle_next():
            self.btn_next.config(state=tk.NORMAL if self.accept_var.get() else tk.DISABLED)
        
        accept_check = ttk.Checkbutton(
            self.content_frame,
            text="I accept the terms in the License Agreement",
            variable=self.accept_var,
            command=toggle_next
        )
        accept_check.pack(anchor=tk.W, pady=(5, 0))
        
        self.btn_back.config(state=tk.NORMAL)
        self.btn_next.config(text="Next >", state=tk.DISABLED)
        
    def folder_page(self):
        ttk.Label(
            self.content_frame,
            text="Destination Folder",
            style='Title.TLabel'
        ).pack(anchor=tk.W, pady=(0, 15))
        
        ttk.Label(
            self.content_frame,
            text="Choose the folder in which to install Deadbolt Endpoint Shield.",
            style='Subtitle.TLabel'
        ).pack(anchor=tk.W, pady=(0, 20))
        
        folder_frame = ttk.Frame(self.content_frame, style='Wizard.TFrame')
        folder_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.install_path = os.path.join(os.environ["ProgramFiles"], "DeadboltEndpointShield")
        
        ttk.Label(folder_frame, text="Folder:", style='Wizard.TLabel').pack(side=tk.LEFT)
        
        self.path_entry = ttk.Entry(folder_frame, font=('Segoe UI', 9))
        self.path_entry.insert(0, self.install_path)
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        
        ttk.Button(folder_frame, text="Browse...", style='Wizard.TButton').pack(side=tk.LEFT)
        
        ttk.Label(
            self.content_frame,
            text="Setup will install Deadbolt Endpoint Shield to the following folder.\nTo continue, click Next.",
            style='Wizard.TLabel'
        ).pack(anchor=tk.W, pady=(20, 0))
        
        self.btn_back.config(state=tk.NORMAL)
        self.btn_next.config(text="Next >", state=tk.NORMAL)
        
    def config_page(self):
        ttk.Label(
            self.content_frame,
            text="Configuration",
            style='Title.TLabel'
        ).pack(anchor=tk.W, pady=(0, 15))
        
        ttk.Label(
            self.content_frame,
            text="Enter the secret key offset that will be used to unlock the system.",
            style='Subtitle.TLabel'
        ).pack(anchor=tk.W, pady=(0, 20))
        
        config_frame = ttk.Frame(self.content_frame, style='Wizard.TFrame')
        config_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(config_frame, text="Secret Key Offset:", style='Wizard.TLabel', font=('Segoe UI', 9, 'bold')).pack(side=tk.LEFT, padx=(0, 10))
        
        self.offset_entry = ttk.Entry(config_frame, font=('Segoe UI', 12), width=15, justify=tk.CENTER)
        self.offset_entry.insert(0, "1050")
        self.offset_entry.pack(side=tk.LEFT)
        
        ttk.Separator(self.content_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=20)
        
        ttk.Label(
            self.content_frame,
            text="This offset will be added to the challenge code to unlock the system.",
            style='Wizard.TLabel'
        ).pack(anchor=tk.W)
        
        self.btn_back.config(state=tk.NORMAL)
        self.btn_next.config(text="Next >", state=tk.NORMAL)
        
    def ready_page(self):
        ttk.Label(
            self.content_frame,
            text="Ready to Install",
            style='Title.TLabel'
        ).pack(anchor=tk.W, pady=(0, 15))
        
        ttk.Label(
            self.content_frame,
            text="Setup is ready to begin the installation.",
            style='Subtitle.TLabel'
        ).pack(anchor=tk.W, pady=(0, 20))
        
        info_frame = tk.LabelFrame(self.content_frame, text="Installation Summary", bg='#ffffff', font=('Segoe UI', 9, 'bold'), padx=15, pady=15)
        info_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(
            info_frame,
            text=f"• Destination: {self.install_path}",
            bg='#ffffff',
            font=('Segoe UI', 9)
        ).pack(anchor=tk.W, pady=3)
        
        tk.Label(
            info_frame,
            text=f"• Secret Key Offset: {self.offset_entry.get()}",
            bg='#ffffff',
            font=('Segoe UI', 9)
        ).pack(anchor=tk.W, pady=3)
        
        ttk.Separator(info_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        tk.Label(
            info_frame,
            text="Click Install to begin the installation.",
            bg='#ffffff',
            font=('Segoe UI', 9)
        ).pack(anchor=tk.W)
        
        self.btn_back.config(state=tk.NORMAL)
        self.btn_next.config(text="Install", state=tk.NORMAL)
        
    def install_page(self):
        ttk.Label(
            self.content_frame,
            text="Installing Deadbolt Endpoint Shield",
            style='Title.TLabel'
        ).pack(anchor=tk.W, pady=(0, 30))
        
        self.progress = ttk.Progressbar(self.content_frame, orient=tk.HORIZONTAL, length=500, mode='determinate')
        self.progress.pack(pady=(0, 20))
        
        self.status_label = ttk.Label(self.content_frame, text="Initializing...", style='Subtitle.TLabel')
        self.status_label.pack(anchor=tk.W)
        
        self.btn_back.config(state=tk.DISABLED)
        self.btn_next.config(state=tk.DISABLED)
        self.btn_cancel.config(state=tk.DISABLED)
        
        self.root.after(300, self.perform_installation)
        
    def perform_installation(self):
        steps = [
            "Creating directories...",
            "Copying files...",
            "Registering components...",
            "Saving configuration...",
            "Finalizing installation..."
        ]
        
        try:
            self.secret_offset = int(self.offset_entry.get())
            self.install_path = self.path_entry.get()
            
            appdata_path = os.path.join(os.environ["ProgramData"], "DeadboltEndpointShield")
            os.makedirs(appdata_path, exist_ok=True)
            os.makedirs(self.install_path, exist_ok=True)
            
            for i, step in enumerate(steps):
                self.status_label.config(text=step)
                self.progress['value'] = (i + 1) / len(steps) * 100
                self.root.update()
                time.sleep(0.9)
            
            config_data = {
                "SecretKeyOffset": self.secret_offset,
                "InstallPath": self.install_path,
                "InstallDate": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "Version": "1.0"
            }
            
            config_path = os.path.join(appdata_path, "config.json")
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=4)
            
            self.root.after(500, lambda: self.show_page(6))
            
        except Exception as ex:
            messagebox.showerror("Installation Error", f"An error occurred:\n{str(ex)}")
            self.cancel()
            
    def complete_page(self):
        ttk.Label(
            self.content_frame,
            text="Completing the Deadbolt Endpoint Shield Setup Wizard",
            style='Title.TLabel'
        ).pack(anchor=tk.W, pady=(0, 20))
        
        ttk.Label(
            self.content_frame,
            text="Deadbolt Endpoint Shield has been successfully installed.",
            style='Subtitle.TLabel'
        ).pack(anchor=tk.W, pady=(0, 30))
        
        self.launch_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            self.content_frame,
            text="Launch Deadbolt Endpoint Shield",
            variable=self.launch_var
        ).pack(anchor=tk.W, pady=5)
        
        ttk.Label(
            self.content_frame,
            text="Click Finish to close Setup.",
            style='Wizard.TLabel'
        ).pack(anchor=tk.W, pady=(30, 0))
        
        self.btn_back.config(state=tk.DISABLED)
        self.btn_next.config(text="Finish", state=tk.NORMAL, command=self.finish)
        self.btn_cancel.config(state=tk.DISABLED)
        
    def next_page(self):
        if self.current_page < len(self.pages) - 1:
            self.show_page(self.current_page + 1)
            
    def prev_page(self):
        if self.current_page > 0:
            self.show_page(self.current_page - 1)
            
    def cancel(self):
        if messagebox.askyesno("Cancel Setup", "Are you sure you want to cancel Deadbolt Endpoint Shield Setup?"):
            self.root.destroy()
            
    def finish(self):
        self.root.destroy()
        if self.launch_var.get():
            print("Launching Deadbolt...")
            messagebox.showinfo("Deadbolt Endpoint Shield", "Setup complete! Deadbolt is ready to use!")

def main():
    root = tk.Tk()
    
    try:
        root.iconbitmap(default='')
    except:
        pass
    
    app = ModernInstallerWizard(root)
    root.mainloop()

if __name__ == "__main__":
    main()
