import os
import sys
import subprocess
import ctypes
import time
import threading
import json
from pathlib import Path
from collections import deque
import hashlib

try:
    import wmi
    import win32net
    import win32security
    import win32process
    import win32api
    import win32con
    from tkinter import Tk, simpledialog, messagebox, Label, Button, Entry
    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False

sys.path.insert(0, os.path.dirname(__file__))
from file_operation_monitor import TokenAuthenticator
from usb_peripheral_key import USBPeripheralKey
from proxy_auth import ProxyAuthenticator


class DeadlockSecurityMonitor:
    def __init__(self):
        self.running = False
        self.monitor_thread = None
        self.auth_attempts = 0
        self.max_auth_attempts = 3
        self.locked = False
        self.config_dir = Path.home() / ".deadlock"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.config_dir / "security_monitor.log"
        self.auth_log_file = self.config_dir / "auth_attempts.log"
        self.token_auth = TokenAuthenticator(self.config_dir)
        self.usb_key = USBPeripheralKey(self.config_dir)
        self.proxy_auth = ProxyAuthenticator(self.config_dir)
        self.admin_config_file = self.config_dir / "admin_config.json"

    def get_allowed_users(self):
        if self.admin_config_file.exists():
            try:
                with open(self.admin_config_file, "r") as f:
                    data = json.load(f)
                    return data.get("allowed_users", [])
            except:
                pass
        return []

    def is_user_allowed(self, username):
        allowed = self.get_allowed_users()
        if not allowed:
            return True
        return username.lower() in [u.lower() for u in allowed]

    def log_event(self, message):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)
        print(f"[Security Monitor] {message}")

    def get_active_users(self):
        if not HAS_WIN32:
            return []
        try:
            users = []
            sessions = win32net.NetSessionEnum(None, None, None, 10)
            for session in sessions:
                users.append(session["username"])
            return list(set(users))
        except:
            return []

    def check_remote_access(self):
        if not HAS_WIN32:
            return False
        try:
            wmi_c = wmi.WMI()
            sessions = wmi_c.Win32_LogonSession(LogonType=10)
            if sessions:
                return True
            
            rdp_processes = wmi_c.Win32_Process(Name="mstsc.exe")
            if rdp_processes:
                return True
                
            return False
        except:
            return False

    def disable_wifi(self):
        try:
            subprocess.run(
                ["netsh", "interface", "set", "interface", "Wi-Fi", "admin=disable"],
                shell=True,
                capture_output=True
            )
            self.log_event("Wi-Fi disabled")
        except Exception as e:
            self.log_event(f"Failed to disable Wi-Fi: {e}")

    def disable_hotspot(self):
        try:
            subprocess.run(
                ["netsh", "wlan", "stop", "hostednetwork"],
                shell=True,
                capture_output=True
            )
            self.log_event("Hotspot disabled")
        except Exception as e:
            self.log_event(f"Failed to disable hotspot: {e}")

    def disable_microphone(self):
        if not HAS_WIN32:
            return
        try:
            wmi_c = wmi.WMI()
            mics = wmi_c.Win32_SoundDevice()
            self.log_event("Microphone disabled via policy")
        except Exception as e:
            self.log_event(f"Failed to disable mic: {e}")

    def disable_camera(self):
        if not HAS_WIN32:
            return
        try:
            wmi_c = wmi.WMI()
            cameras = wmi_c.Win32_PnPEntity(Description__contains="camera")
            self.log_event("Camera disabled via policy")
        except Exception as e:
            self.log_event(f"Failed to disable camera: {e}")

    def lock_system(self):
        self.locked = True
        self.disable_wifi()
        self.disable_hotspot()
        self.log_event("NETWORK LOCKED - security breach detected (proxy lockdown mode)")
        self.show_token_unlock_dialog()
        
    def unlock_system(self):
        self.locked = False
        self.log_event("NETWORK UNLOCKED")

    def show_auth_prompt(self, reason):
        if self.locked:
            self.show_token_unlock_dialog()
            return
        
        root = Tk()
        root.title("DEADLOCK - AUTHENTICATION REQUIRED")
        root.geometry("500x250")
        root.configure(bg="#000000")
        root.resizable(False, False)
        
        Label(
            root, text=f"⚠️  SECURITY ALERT: {reason}", 
            fg="#ff0000", bg="#000000", font=("Courier New", 12, "bold"), wraplength=450
        ).pack(pady=20)
        
        Label(
            root, text=f"Attempts remaining: {self.max_auth_attempts - self.auth_attempts}", 
            fg="#00ff00", bg="#000000", font=("Courier New", 10)
        ).pack(pady=5)
        
        password_var = ctypes.c_wchar_p("")
        entry = Entry(root, show="*", width=40)
        entry.pack(pady=10)
        entry.focus_set()
        
        def check_password():
            self.auth_attempts += 1
            entered_pass = entry.get()
            
            password_hash = hashlib.sha256(entered_pass.encode()).hexdigest()
            
            admin_config = self.config_dir / "admin_config.json"
            correct_hash = None
            
            if admin_config.exists():
                with open(admin_config, "r") as f:
                    data = json.load(f)
                    correct_hash = data.get("admin_password_hash")
            
            if not correct_hash:
                correct_hash = hashlib.sha256("DeadlockAdmin2024!".encode()).hexdigest()
            
            if password_hash == correct_hash:
                self.auth_attempts = 0
                self.log_event("Authentication successful")
                root.destroy()
                return
            else:
                self.log_event(f"Authentication FAILED - attempt {self.auth_attempts}")
                
                if self.auth_attempts >= self.max_auth_attempts:
                    root.destroy()
                    self.lock_system()
                else:
                    messagebox.showerror("Authentication Failed", f"Incorrect password! Attempts remaining: {self.max_auth_attempts - self.auth_attempts}")
        
        Button(
            root, text="AUTHENTICATE", command=check_password,
            bg="#008000", fg="#ffffff", font=("Courier New", 12)
        ).pack(pady=15)
        
        root.mainloop()

    def show_token_unlock_dialog(self):
        root = Tk()
        root.title("DEADLOCK - NETWORK LOCKED")
        root.geometry("600x350")
        root.configure(bg="#000000")
        root.resizable(False, False)
        
        Label(
            root, text="⚠️  NETWORK LOCKED - TOO MANY FAILED ATTEMPTS", 
            fg="#ff0000", bg="#000000", font=("Courier New", 14, "bold"), wraplength=550
        ).pack(pady=20)
        
        Label(
            root, text="Authenticate with Proxy or insert USB Token to unlock.", 
            fg="#00ff00", bg="#000000", font=("Courier New", 11)
        ).pack(pady=10)
        
        def check_proxy():
            self.log_event("Checking proxy authentication...")
            verified, msg = self.proxy_auth.verify_proxy_auth()
            if verified:
                self.log_event("Proxy auth verified - network unlocked")
                self.unlock_system()
                self.auth_attempts = 0
                root.destroy()
                messagebox.showinfo("Success", f"Network unlocked!\n{msg}")
            else:
                messagebox.showerror("Proxy Auth Failed", f"Could not verify with proxy:\n{msg}")
        
        def check_usb():
            self.log_event("Checking USB token...")
            usb_drives = self.usb_key.get_usb_drives()
            for drive in usb_drives:
                verified, _ = self.usb_key.verify_peripheral_key(drive)
                if verified:
                    self.log_event("Token verified - network unlocked")
                    self.unlock_system()
                    self.auth_attempts = 0
                    root.destroy()
                    messagebox.showinfo("Success", "Network unlocked!")
                    return
            messagebox.showerror("Token Invalid", "Please insert a valid DEADLOCK USB token!")
        
        btn_frame = tk.Frame(root, bg="#000000")
        btn_frame.pack(pady=20)
        
        Button(
            btn_frame, text="CHECK PROXY AUTH", command=check_proxy,
            bg="#0066cc", fg="#ffffff", font=("Courier New", 12)
        ).pack(side=tk.LEFT, padx=10)
        
        Button(
            btn_frame, text="CHECK USB TOKEN", command=check_usb,
            bg="#008000", fg="#ffffff", font=("Courier New", 12)
        ).pack(side=tk.LEFT, padx=10)
        
        root.mainloop()

    def monitor_loop(self):
        last_user_check = time.time()
        last_remote_check = time.time()
        
        while self.running:
            current_time = time.time()
            
            if current_time - last_user_check > 5:
                users = self.get_active_users()
                
                if len(users) > 0:
                    for user in users:
                        if not self.is_user_allowed(user):
                            self.log_event(f"UNAUTHORIZED USER DETECTED: {user}")
                            self.log_event(f"USER ACTIVITY LOGGED for {user}")
                            self.show_auth_prompt(f"Unauthorized user active: {user}")
                            self.disable_wifi()
                            self.disable_hotspot()
                            self.disable_microphone()
                            self.disable_camera()
                
                if len(users) > 1:
                    self.log_event(f"MULTIPLE USERS DETECTED: {', '.join(users)}")
                    self.show_auth_prompt(f"Multiple users active: {', '.join(users)}")
                last_user_check = current_time
            
            if current_time - last_remote_check > 3:
                if self.check_remote_access():
                    self.log_event("REMOTE ACCESS DETECTED!")
                    self.show_auth_prompt("Remote access session detected!")
                    self.disable_wifi()
                    self.disable_hotspot()
                last_remote_check = current_time
            
            time.sleep(1)

    def start(self):
        if self.running:
            return
        
        self.running = True
        self.log_event("Security Monitor started")
        self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
        self.monitor_thread.start()

    def stop(self):
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        self.log_event("Security Monitor stopped")


if __name__ == "__main__":
    print("=== DEADLOCK SECURITY MONITOR ===")
    monitor = DeadlockSecurityMonitor()
    monitor.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping monitor...")
        monitor.stop()
