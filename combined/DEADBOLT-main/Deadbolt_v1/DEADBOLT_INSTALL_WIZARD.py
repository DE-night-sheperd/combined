import os
import sys
import time
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from usb_peripheral_key import USBPeripheralKey
from security_utils import SecurityUtils
from file_operation_monitor import TokenAuthenticator

WIN98_BG = "#c0c0c0"
WIN98_TITLE_BAR = "#000080"
WIN98_TITLE_TEXT = "#ffffff"
WIN98_BUTTON_FACE = "#c0c0c0"
WIN98_BLACK = "#000000"

class DeadboltInstallWizard:
    def __init__(self, root):
        self.root = root
        self.root.title("Deadbolt - Setup Wizard")
        self.root.geometry("650x500")
        self.root.configure(bg=WIN98_BG)
        self.root.resizable(False, False)
        
        self.config_dir = Path.home() / ".deadbolt"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        SecurityUtils.secure_config_directory(self.config_dir)
        
        self.usb_key = USBPeripheralKey(self.config_dir)
        self.token_auth = TokenAuthenticator(self.config_dir)
        
        self.selected_usb = None
        self.token_key = None
        
        self.current_step = 0
        self.steps = [
            self.show_welcome,
            self.show_usb_insertion,
            self.show_token_setup,
            self.show_key_generation,
            self.show_complete
        ]
        
        self.setup_ui()
        self.show_current_step()
        
    def setup_ui(self):
        title_frame = tk.Frame(self.root, bg=WIN98_TITLE_BAR, height=30)
        title_frame.pack(fill=tk.X)
        
        tk.Label(
            title_frame,
            text="  Deadbolt Endpoint Shield - Setup",
            font=("MS Sans Serif", 10, "bold"),
            bg=WIN98_TITLE_BAR,
            fg=WIN98_TITLE_TEXT
        ).pack(side=tk.LEFT, pady=5)
        
        self.content_frame = tk.Frame(self.root, bg=WIN98_BG, padx=30, pady=30)
        self.content_frame.pack(fill=tk.BOTH, expand=True)
        
        self.nav_frame = tk.Frame(self.root, bg=WIN98_BG, padx=30, pady=15)
        self.nav_frame.pack(fill=tk.X)
        
        self.btn_back = tk.Button(
            self.nav_frame,
            text="< Back",
            bg=WIN98_BUTTON_FACE,
            fg=WIN98_BLACK,
            relief=tk.RAISED,
            bd=2,
            padx=8,
            pady=4,
            font=("MS Sans Serif", 8),
            command=self.previous_step
        )
        self.btn_back.pack(side=tk.LEFT, padx=5)
        
        self.btn_next = tk.Button(
            self.nav_frame,
            text="Next >",
            bg=WIN98_BUTTON_FACE,
            fg=WIN98_BLACK,
            relief=tk.RAISED,
            bd=2,
            padx=8,
            pady=4,
            font=("MS Sans Serif", 8),
            command=self.next_step
        )
        self.btn_next.pack(side=tk.RIGHT, padx=5)
        
        self.btn_cancel = tk.Button(
            self.nav_frame,
            text="Cancel",
            bg=WIN98_BUTTON_FACE,
            fg=WIN98_BLACK,
            relief=tk.RAISED,
            bd=2,
            padx=8,
            pady=4,
            font=("MS Sans Serif", 8),
            command=self.root.quit
        )
        self.btn_cancel.pack(side=tk.RIGHT, padx=5)
        
    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
    def show_current_step(self):
        self.clear_content()
        self.steps[self.current_step]()
        self.update_nav_buttons()
        
    def update_nav_buttons(self):
        self.btn_back.config(state=tk.NORMAL if self.current_step > 0 else tk.DISABLED)
        if self.current_step == len(self.steps) - 1:
            self.btn_next.config(text="Finish")
        else:
            self.btn_next.config(text="Next >")
            
    def next_step(self):
        if self.current_step == 1:
            try:
                if hasattr(self, 'usb_listbox') and self.usb_listbox.winfo_exists():
                    selection = self.usb_listbox.curselection()
                    if selection:
                        selected = self.usb_listbox.get(selection[0])
                        if "(No USB" not in selected:
                            self.selected_usb = selected
            except:
                pass
        
        if self.current_step < len(self.steps) - 1:
            self.current_step += 1
            self.show_current_step()
        else:
            self.root.quit()
            
    def previous_step(self):
        if self.current_step > 0:
            self.current_step -= 1
            self.show_current_step()
            
    def show_welcome(self):
        tk.Label(
            self.content_frame,
            text="Welcome to Deadbolt",
            font=("MS Sans Serif", 16, "bold"),
            bg=WIN98_BG,
            fg=WIN98_BLACK
        ).pack(pady=(20, 30))
        
        tk.Label(
            self.content_frame,
            text="This wizard will guide you through the setup of\nDeadbolt Endpoint Shield.",
            font=("MS Sans Serif", 10),
            bg=WIN98_BG,
            fg=WIN98_BLACK,
            justify=tk.CENTER
        ).pack()
        
        tk.Label(
            self.content_frame,
            text="\n• USB Peripheral Key Generation\n• Level 1 Token Key Setup\n• System Configuration",
            font=("MS Sans Serif", 9),
            bg=WIN98_BG,
            fg=WIN98_BLACK,
            justify=tk.LEFT
        ).pack(pady=20)
        
    def show_usb_insertion(self):
        tk.Label(
            self.content_frame,
            text="Step 2: Insert USB Drive",
            font=("MS Sans Serif", 14, "bold"),
            bg=WIN98_BG,
            fg=WIN98_BLACK
        ).pack(pady=(10, 20))
        
        tk.Label(
            self.content_frame,
            text="Please insert a USB drive to generate a\nmachine-specific peripheral key.",
            font=("MS Sans Serif", 10),
            bg=WIN98_BG,
            fg=WIN98_BLACK,
            justify=tk.CENTER
        ).pack(pady=10)
        
        self.usb_listbox = tk.Listbox(self.content_frame, font=("MS Sans Serif", 9), height=8)
        self.usb_listbox.pack(fill=tk.X, pady=10)
        
        btn_frame = tk.Frame(self.content_frame, bg=WIN98_BG)
        btn_frame.pack(pady=10)
        
        tk.Button(
            btn_frame,
            text="🔄 Refresh",
            bg=WIN98_BUTTON_FACE,
            fg=WIN98_BLACK,
            relief=tk.RAISED,
            bd=2,
            padx=8,
            pady=4,
            font=("MS Sans Serif", 8),
            command=self.refresh_usb_list
        ).pack(side=tk.LEFT, padx=5)
        
        self.refresh_usb_list()
        
    def refresh_usb_list(self):
        self.usb_listbox.delete(0, tk.END)
        drives = self.usb_key.get_usb_drives()
        if drives:
            for drive in drives:
                self.usb_listbox.insert(tk.END, drive)
            self.usb_listbox.selection_set(0)
        else:
            self.usb_listbox.insert(tk.END, "(No USB drives detected)")
            
    def show_token_setup(self):
        try:
            if hasattr(self, 'usb_listbox') and self.usb_listbox.winfo_exists():
                selection = self.usb_listbox.curselection()
                if selection:
                    selected = self.usb_listbox.get(selection[0])
                    if "(No USB" not in selected:
                        self.selected_usb = selected
        except:
            pass
        
        if not self.selected_usb:
            messagebox.showwarning("Warning", "Please select a USB drive first!", parent=self.root)
            self.current_step -= 1
            self.show_current_step()
            return
            
        tk.Label(
            self.content_frame,
            text="Step 3: Set Level 1 Token Key",
            font=("MS Sans Serif", 14, "bold"),
            bg=WIN98_BG,
            fg=WIN98_BLACK
        ).pack(pady=(10, 20))
        
        tk.Label(
            self.content_frame,
            text="Password Requirements:",
            font=("MS Sans Serif", 10, "bold"),
            bg=WIN98_BG,
            fg=WIN98_BLACK
        ).pack(anchor=tk.W)
        
        req_frame = tk.Frame(self.content_frame, bg=WIN98_BG, bd=2, relief=tk.SUNKEN)
        req_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(req_frame, text="• Minimum 8 characters long", bg=WIN98_BG, fg=WIN98_BLACK, font=("MS Sans Serif", 9)).pack(anchor=tk.W, padx=10, pady=2)
        tk.Label(req_frame, text="• At least one uppercase letter", bg=WIN98_BG, fg=WIN98_BLACK, font=("MS Sans Serif", 9)).pack(anchor=tk.W, padx=10, pady=2)
        tk.Label(req_frame, text="• At least one lowercase letter", bg=WIN98_BG, fg=WIN98_BLACK, font=("MS Sans Serif", 9)).pack(anchor=tk.W, padx=10, pady=2)
        tk.Label(req_frame, text="• At least one digit", bg=WIN98_BG, fg=WIN98_BLACK, font=("MS Sans Serif", 9)).pack(anchor=tk.W, padx=10, pady=2)
        
        tk.Label(self.content_frame, text="Enter Token Key:", bg=WIN98_BG, fg=WIN98_BLACK, font=("MS Sans Serif", 10, "bold")).pack(anchor=tk.W, pady=(15,5))
        self.token1_var = tk.StringVar()
        tk.Entry(self.content_frame, textvariable=self.token1_var, show="*", font=("MS Sans Serif", 10), width=40).pack(fill=tk.X, pady=5)
        
        tk.Label(self.content_frame, text="Confirm Token Key:", bg=WIN98_BG, fg=WIN98_BLACK, font=("MS Sans Serif", 10, "bold")).pack(anchor=tk.W, pady=(15,5))
        self.token2_var = tk.StringVar()
        tk.Entry(self.content_frame, textvariable=self.token2_var, show="*", font=("MS Sans Serif", 10), width=40).pack(fill=tk.X, pady=5)
        
    def show_key_generation(self):
        if not hasattr(self, 'token1_var') or not hasattr(self, 'token2_var'):
            self.current_step -= 1
            self.show_current_step()
            return
            
        t1 = self.token1_var.get()
        t2 = self.token2_var.get()
        
        if t1 != t2:
            messagebox.showerror("Error", "Token keys do not match!", parent=self.root)
            self.current_step -= 1
            self.show_current_step()
            return
            
        try:
            self.token_auth.set_token(t1)
            self.token_key = t1
        except ValueError as e:
            messagebox.showerror("Weak Password", str(e), parent=self.root)
            self.current_step -= 1
            self.show_current_step()
            return
            
        tk.Label(
            self.content_frame,
            text="Step 4: Generate Peripheral Key",
            font=("MS Sans Serif", 14, "bold"),
            bg=WIN98_BG,
            fg=WIN98_BLACK
        ).pack(pady=(10, 20))
        
        tk.Label(
            self.content_frame,
            text=f"Selected USB Drive: {self.selected_usb}",
            font=("MS Sans Serif", 10),
            bg=WIN98_BG,
            fg=WIN98_BLACK
        ).pack(pady=5)
        
        tk.Label(
            self.content_frame,
            text="\nClick 'Generate Key' to create a machine-specific\nperipheral key on the USB drive.",
            font=("MS Sans Serif", 10),
            bg=WIN98_BG,
            fg=WIN98_BLACK,
            justify=tk.CENTER
        ).pack(pady=15)
        
        self.progress_frame = tk.Frame(self.content_frame, bg=WIN98_BG)
        self.progress_frame.pack(fill=tk.X, pady=10)
        
        self.progress_label = tk.Label(
            self.progress_frame,
            text="Ready",
            font=("MS Sans Serif", 9),
            bg=WIN98_BG,
            fg=WIN98_BLACK
        )
        self.progress_label.pack(anchor=tk.W)
        
        self.progress_bar = ttk.Progressbar(
            self.progress_frame,
            orient=tk.HORIZONTAL,
            length=400,
            mode='determinate'
        )
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        self.progress_percent = tk.Label(
            self.progress_frame,
            text="0%",
            font=("MS Sans Serif", 9, "bold"),
            bg=WIN98_BG,
            fg=WIN98_BLACK
        )
        self.progress_percent.pack(anchor=tk.E)
        
        btn_frame = tk.Frame(self.content_frame, bg=WIN98_BG)
        btn_frame.pack(pady=15)
        
        self.gen_btn = tk.Button(
            btn_frame,
            text="🔑 Generate Key",
            bg=WIN98_BUTTON_FACE,
            fg=WIN98_BLACK,
            relief=tk.RAISED,
            bd=2,
            padx=8,
            pady=4,
            font=("MS Sans Serif", 8),
            command=self.start_key_generation
        )
        self.gen_btn.pack(side=tk.LEFT, padx=5)
        
        self.key_status = tk.Label(
            self.content_frame,
            text="",
            font=("MS Sans Serif", 9),
            bg=WIN98_BG,
            fg="#008800"
        )
        self.key_status.pack(pady=10)
        
    def start_key_generation(self):
        self.gen_btn.config(state=tk.DISABLED)
        self.key_status.config(text="")
        self.progress_bar['value'] = 0
        self.progress_percent.config(text="0%")
        self.current_progress = 0
        self.gen_steps = [
            (10, "Reading hardware fingerprint..."),
            (25, "Collecting machine identifiers..."),
            (40, "Generating unique machine ID..."),
            (55, "Hashing with SHA-256..."),
            (70, "Creating signature..."),
            (85, "Writing to USB drive..."),
            (95, "Verifying key integrity..."),
            (100, "Complete!")
        ]
        self.gen_step_index = 0
        self.root.after(1200, self.update_progress)
        
    def update_progress(self):
        if self.current_progress < 100:
            self.current_progress += 1
            self.progress_bar['value'] = self.current_progress
            self.progress_percent.config(text=f"{self.current_progress}%")
            
            for i, (target, label) in enumerate(self.gen_steps):
                if self.current_progress >= target and i > self.gen_step_index:
                    self.gen_step_index = i
                    self.progress_label.config(text=label)
            
            self.root.after(1200, self.update_progress)
        else:
            self.finish_key_generation()
        
    def finish_key_generation(self):
        success, msg = self.usb_key.generate_peripheral_key(self.selected_usb)
        if success:
            self.progress_label.config(text="Key generated successfully!")
            self.key_status.config(text=f"✅ {msg}", fg="#008800")
        else:
            self.progress_label.config(text="Key generation failed!")
            self.key_status.config(text=f"❌ {msg}", fg="#880000")
            
    def show_complete(self):
        self.token_auth.mark_first_launch_complete()
        
        tk.Label(
            self.content_frame,
            text="Setup Complete!",
            font=("MS Sans Serif", 18, "bold"),
            bg=WIN98_BG,
            fg="#008800"
        ).pack(pady=(20, 30))
        
        tk.Label(
            self.content_frame,
            text="Deadbolt Endpoint Shield has been successfully set up!",
            font=("MS Sans Serif", 10),
            bg=WIN98_BG,
            fg=WIN98_BLACK
        ).pack(pady=5)
        
        tk.Label(
            self.content_frame,
            text="\n✅ USB Peripheral Key generated\n✅ Level 1 Token Key set\n✅ System configured",
            font=("MS Sans Serif", 10),
            bg=WIN98_BG,
            fg="#008800"
        ).pack(pady=15)
        
        tk.Label(
            self.content_frame,
            text="\nYou may now remove the USB drive.",
            font=("MS Sans Serif", 9, "italic"),
            bg=WIN98_BG,
            fg=WIN98_BLACK
        ).pack(pady=10)

def main():
    root = tk.Tk()
    app = DeadboltInstallWizard(root)
    root.mainloop()

if __name__ == "__main__":
    main()
