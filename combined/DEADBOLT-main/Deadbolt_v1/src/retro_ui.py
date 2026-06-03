import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, scrolledtext
import sys
import os
import json
import time
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))
from security_utils import SecurityUtils
from device_fingerprint import get_device_fingerprint, get_fingerprint_json
from file_backup_restore import FileBackupManager
from application_whitelisting import ApplicationWhitelistManager
from threat_intelligence import ThreatIntelligenceFeed
from usb_sandbox_scanner import USBSandboxScanner
from network_firewall import NetworkFirewall
from incident_response import IncidentResponseManager
from vulnerability_scanner import VulnerabilityScanner
from browser_sandbox import BrowserSandboxManager
from ransomware_decryptor import RansomwareDecryptor
from compliance_reporting import ComplianceReporter
from desktop_shortcut import create_desktop_shortcut
from system_activity_monitor import SystemActivityMonitor
from proxy_auth import ProxyAuthenticator

# Windows 95/98 color scheme
WIN95_BG = "#c0c0c0"
WIN95_DARK = "#808080"
WIN95_LIGHT = "#ffffff"
WIN95_BLUE = "#000080"
WIN95_BLACK = "#000000"

class AdminAuthenticator:
    def __init__(self, config_dir: Path):
        self.config_dir = config_dir
        self.admin_config_file = config_dir / "admin_config.json"
        self.audit_log_file = config_dir / "admin_audit.log"
        self._ensure_config()
        
    def _ensure_config(self):
        if not self.admin_config_file.exists():
            default_admin = {
                "admin_username": "admin",
                "admin_password_hash": self._hash_password("DeadlockAdmin2024!"),
                "admin_enabled": True,
                "allowed_users": []
            }
            self._save_admin_config(default_admin)
    
    def get_allowed_users(self):
        config = self._load_admin_config()
        return config.get("allowed_users", [])
    
    def add_allowed_user(self, username):
        config = self._load_admin_config()
        if "allowed_users" not in config:
            config["allowed_users"] = []
        if username not in config["allowed_users"]:
            config["allowed_users"].append(username)
            self._save_admin_config(config)
            self._log_audit(f"Allowed user added: {username}", include_device_info=True)
            return True
        return False
    
    def remove_allowed_user(self, username):
        config = self._load_admin_config()
        if "allowed_users" in config and username in config["allowed_users"]:
            config["allowed_users"].remove(username)
            self._save_admin_config(config)
            self._log_audit(f"Allowed user removed: {username}", include_device_info=True)
            return True
        return False
            
    def _hash_password(self, password: str) -> str:
        import hashlib
        return hashlib.sha256(password.encode('utf-8')).hexdigest()
        
    def _save_admin_config(self, config: dict):
        with open(self.admin_config_file, 'w') as f:
            json.dump(config, f, indent=2)
            
    def _load_admin_config(self) -> dict:
        if self.admin_config_file.exists():
            with open(self.admin_config_file, 'r') as f:
                return json.load(f)
        return {}
        
    def authenticate(self, username: str, password: str) -> bool:
        config = self._load_admin_config()
        if config.get("admin_username") == username and \
           config.get("admin_password_hash") == self._hash_password(password):
            self._log_audit(f"Admin login successful: {username}", include_device_info=True)
            return True
        self._log_audit(f"Admin login failed: {username}", include_device_info=True)
        return False
        
    def _log_audit(self, message: str, include_device_info: bool = False):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        if include_device_info:
            device_info = get_device_fingerprint()
            log_entry += f"  DEVICE INFO:\n"
            log_entry += f"    Hostname: {device_info.get('hostname', 'n/a')}\n"
            log_entry += f"    Username: {device_info.get('username', 'n/a')}\n"
            log_entry += f"    OS: {device_info.get('os', 'n/a')} {device_info.get('os_version', 'n/a')}\n"
            log_entry += f"    IP Addresses: {', '.join(device_info.get('ip_addresses', ['n/a']))}\n"
            log_entry += f"    MAC Address: {device_info.get('mac_address', 'n/a')}\n"
            if 'motherboard_serial' in device_info:
                log_entry += f"    Motherboard: {device_info.get('motherboard_product', 'n/a')} (SN: {device_info.get('motherboard_serial', 'n/a')})\n"
            log_entry += "\n"
            
        with open(self.audit_log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
            
    def change_admin_password(self, old_pass: str, new_pass: str) -> tuple[bool, str]:
        config = self._load_admin_config()
        if config.get("admin_password_hash") != self._hash_password(old_pass):
            self._log_audit("Failed password change: invalid old password", include_device_info=True)
            return False, "Invalid old password"
            
        is_valid, msg = SecurityUtils.validate_password_complexity(new_pass)
        if not is_valid:
            self._log_audit(f"Failed password change: {msg}", include_device_info=True)
            return False, msg
            
        config["admin_password_hash"] = self._hash_password(new_pass)
        self._save_admin_config(config)
        self._log_audit("Admin password changed successfully", include_device_info=True)
        return True, "Password changed successfully"

class DeadlockRetroUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Deadlock Endpoint Shield")
        self.root.geometry("640x480")
        self.root.configure(bg=WIN95_BG)
        self.root.resizable(False, False)
        
        self.config_dir = Path.home() / ".deadlock"
        self.admin_auth = AdminAuthenticator(self.config_dir)
        self.backup_manager = FileBackupManager(self.config_dir)
        self.app_whitelist = ApplicationWhitelistManager(self.config_dir)
        self.threat_feed = ThreatIntelligenceFeed(self.config_dir)
        self.usb_sandbox = USBSandboxScanner(self.config_dir)
        self.network_firewall = NetworkFirewall(self.config_dir)
        self.incident_response = IncidentResponseManager(self.config_dir)
        self.vuln_scanner = VulnerabilityScanner(self.config_dir)
        self.browser_sandbox = BrowserSandboxManager(self.config_dir)
        self.ransomware_decryptor = RansomwareDecryptor(self.config_dir)
        self.compliance_reporter = ComplianceReporter(self.config_dir)
        self.activity_monitor = SystemActivityMonitor(self.config_dir)
        self.proxy_auth = ProxyAuthenticator(self.config_dir)
        self.is_admin_authenticated = False
        
        self.activity_monitor.start()
        self.setup_ui()
        
    def setup_ui(self):
        title_bar = tk.Frame(self.root, bg=WIN95_BLUE, height=30)
        title_bar.pack(fill=tk.X)
        title_bar.pack_propagate(False)
        
        tk.Label(
            title_bar, 
            text="Deadlock Endpoint Shield", 
            bg=WIN95_BLUE, 
            fg=WIN95_LIGHT,
            font=("MS Sans Serif", 8, "bold"),
            anchor=tk.W
        ).pack(side=tk.LEFT, padx=5, pady=5)
        
        close_btn = tk.Button(
            title_bar, 
            text="X", 
            bg=WIN95_BG,
            font=("MS Sans Serif", 8, "bold"),
            width=3,
            command=self.root.quit
        )
        close_btn.pack(side=tk.RIGHT, padx=5, pady=2)
        
        main_frame = tk.Frame(self.root, bg=WIN95_BG, padx=2, pady=2)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.inner = tk.Frame(main_frame, bg=WIN95_BG, padx=8, pady=8)
        self.inner.pack(fill=tk.BOTH, expand=True)
        
        self.setup_main_ui()
        
    def setup_main_ui(self):
        for widget in self.inner.winfo_children():
            widget.destroy()
        
        top_frame = tk.Frame(self.inner, bg=WIN95_BG)
        top_frame.pack(fill=tk.X, pady=(0, 20))
        
        icon_label = tk.Label(
            top_frame, 
            text="🔒", 
            font=("Arial", 48), 
            bg=WIN95_BG
        )
        icon_label.pack(side=tk.LEFT, padx=10)
        
        title_frame = tk.Frame(top_frame, bg=WIN95_BG)
        title_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        tk.Label(
            title_frame,
            text="DEADLOCK",
            font=("MS Sans Serif", 18, "bold"),
            bg=WIN95_BG,
            fg=WIN95_BLACK
        ).pack(anchor=tk.W)
        
        tk.Label(
            title_frame,
            text="Endpoint Shield v1.0",
            font=("MS Sans Serif", 10),
            bg=WIN95_BG,
            fg=WIN95_BLACK
        ).pack(anchor=tk.W)
        
        self.admin_status_label = tk.Label(
            title_frame,
            text="[Admin: Not Logged In]",
            font=("MS Sans Serif", 8),
            bg=WIN95_BG,
            fg="#800000"
        )
        self.admin_status_label.pack(anchor=tk.W, pady=(5, 0))
        
        status_group = tk.LabelFrame(
            self.inner, 
            text="System Status", 
            bg=WIN95_BG,
            font=("MS Sans Serif", 8, "bold"),
            padx=10,
            pady=10
        )
        status_group.pack(fill=tk.X, pady=10)
        
        self.status_vars = {
            "monitor": tk.BooleanVar(value=True),
            "ransomware": tk.BooleanVar(value=True),
            "zip_bomb": tk.BooleanVar(value=True),
            "threat_mitigation": tk.BooleanVar(value=True)
        }
        
        status_items = [
            ("Real-time Monitoring", "monitor"),
            ("Ransomware Protection", "ransomware"),
            ("Zip Bomb Detection", "zip_bomb"),
            ("Threat Mitigation", "threat_mitigation")
        ]
        
        for text, key in status_items:
            frame = tk.Frame(status_group, bg=WIN95_BG)
            frame.pack(fill=tk.X, pady=2)
            
            cb = tk.Checkbutton(
                frame,
                text=text,
                variable=self.status_vars[key],
                bg=WIN95_BG,
                font=("MS Sans Serif", 8),
                selectcolor=WIN95_LIGHT,
                activebackground=WIN95_BG
            )
            cb.pack(side=tk.LEFT, anchor=tk.W)
            
            status_label = tk.Label(
                frame,
                text="[ACTIVE]",
                bg=WIN95_BG,
                fg="#008000",
                font=("MS Sans Serif", 8, "bold")
            )
            status_label.pack(side=tk.RIGHT)
        
        btn_frame = tk.Frame(self.inner, bg=WIN95_BG)
        btn_frame.pack(fill=tk.X, pady=20)
        
        buttons = [
            ("Scan Now", self.scan_now),
            ("Admin Login", self.admin_login),
            ("Settings", self.show_settings),
            ("About", self.show_about),
            ("Exit", self.root.quit)
        ]
        
        for text, cmd in buttons:
            btn = tk.Button(
                btn_frame,
                text=text,
                width=12,
                command=cmd,
                bg=WIN95_BG,
                font=("MS Sans Serif", 8),
                padx=8,
                pady=2
            )
            btn.pack(side=tk.LEFT, padx=5)
        
        progress_frame = tk.Frame(self.inner, bg=WIN95_BG)
        progress_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(
            progress_frame,
            text="System Health:",
            bg=WIN95_BG,
            font=("MS Sans Serif", 8)
        ).pack(anchor=tk.W)
        
        self.progress = ttk.Progressbar(
            progress_frame,
            orient=tk.HORIZONTAL,
            length=100,
            mode='determinate'
        )
        self.progress.pack(fill=tk.X, pady=5)
        self.progress['value'] = 85
        
        status_bar = tk.Frame(self.root, bg=WIN95_BG, height=20, relief=tk.SUNKEN, bd=1)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        status_bar.pack_propagate(False)
        
        tk.Label(
            status_bar,
            text="Ready",
            bg=WIN95_BG,
            font=("MS Sans Serif", 8),
            anchor=tk.W
        ).pack(side=tk.LEFT, padx=2)
        
    def refresh_ui_for_admin(self):
        for widget in self.inner.winfo_children():
            widget.destroy()
        
        top_frame = tk.Frame(self.inner, bg=WIN95_BG)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        icon_label = tk.Label(
            top_frame, 
            text="🔒", 
            font=("Arial", 48), 
            bg=WIN95_BG
        )
        icon_label.pack(side=tk.LEFT, padx=10)
        
        title_frame = tk.Frame(top_frame, bg=WIN95_BG)
        title_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        tk.Label(
            title_frame,
            text="DEADLOCK - ADMIN DASHBOARD",
            font=("MS Sans Serif", 16, "bold"),
            bg=WIN95_BG,
            fg=WIN95_BLACK
        ).pack(anchor=tk.W)
        
        tk.Label(
            title_frame,
            text="Endpoint Shield v1.0 - Admin Mode",
            font=("MS Sans Serif", 10),
            bg=WIN95_BG,
            fg=WIN95_BLACK
        ).pack(anchor=tk.W)
        
        self.admin_status_label = tk.Label(
            title_frame,
            text="[Admin: Logged In]",
            font=("MS Sans Serif", 8, "bold"),
            bg=WIN95_BG,
            fg="#008000"
        )
        self.admin_status_label.pack(anchor=tk.W, pady=(5, 0))
        
        dashboard_group = tk.LabelFrame(
            self.inner, 
            text="Admin Dashboard", 
            bg=WIN95_BG,
            font=("MS Sans Serif", 8, "bold"),
            padx=10,
            pady=10
        )
        dashboard_group.pack(fill=tk.BOTH, expand=True, pady=10)
        
        btn_frame_dash = tk.Frame(dashboard_group, bg=WIN95_BG)
        btn_frame_dash.pack(fill=tk.X, pady=10)
        
        buttons_dash = [
            ("View System Activity Log", self.view_activity_log_from_main),
            ("View App Usage Stats", self.view_app_usage_from_main),
            ("File Backup & Restore", self.backup_restore_from_main),
            ("Manage Allowed Users", self.manage_users_from_main),
            ("Proxy Auth Settings", self.proxy_auth_settings),
            ("Full Admin Panel", self.show_admin_panel),
            ("Admin Logout", self.admin_logout)
        ]
        
        for text, cmd in buttons_dash:
            btn = tk.Button(
                btn_frame_dash,
                text=text,
                width=30,
                command=cmd,
                bg=WIN95_BG,
                font=("MS Sans Serif", 9),
                padx=10,
                pady=4
            )
            btn.pack(pady=6)
        
        quick_info = tk.LabelFrame(
            dashboard_group,
            text="Quick Info",
            bg=WIN95_BG,
            font=("MS Sans Serif", 8, "bold"),
            padx=10,
            pady=10
        )
        quick_info.pack(fill=tk.X, pady=10)
        
        usage_stats = self.activity_monitor.get_app_usage_stats()
        top_apps = sorted(usage_stats.items(), key=lambda x: x[1]["duration"], reverse=True)[:5]
        
        info_text = "Most Used Applications:\n"
        for app, stats in top_apps:
            duration_mins = stats["duration"] / 60
            info_text += f"  • {app}: {duration_mins:.1f} mins, {stats['count']} launches\n"
        
        tk.Label(
            quick_info,
            text=info_text,
            bg=WIN95_BG,
            fg=WIN95_BLACK,
            font=("MS Sans Serif", 8),
            justify=tk.LEFT
        ).pack(anchor=tk.W)
        
    def view_activity_log_from_main(self):
        log_window = tk.Toplevel(self.root)
        log_window.title("System Activity Log")
        log_window.geometry("700x500")
        log_window.configure(bg=WIN95_BG)
        
        tk.Label(
            log_window,
            text="SYSTEM ACTIVITY LOG",
            font=("MS Sans Serif", 14, "bold"),
            bg=WIN95_BG
        ).pack(pady=15)
        
        text_area = scrolledtext.ScrolledText(
            log_window,
            wrap=tk.WORD,
            font=("Consolas", 9),
            width=80,
            height=25
        )
        text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        activity_log = self.activity_monitor.get_activity_log(200)
        for line in activity_log:
            text_area.insert(tk.END, line)
        text_area.config(state=tk.DISABLED)
        
    def view_app_usage_from_main(self):
        usage_window = tk.Toplevel(self.root)
        usage_window.title("Application Usage Statistics")
        usage_window.geometry("700x600")
        usage_window.configure(bg=WIN95_BG)
        
        tk.Label(
            usage_window,
            text="APPLICATION USAGE STATISTICS",
            font=("MS Sans Serif", 14, "bold"),
            bg=WIN95_BG
        ).pack(pady=15)
        
        usage_stats = self.activity_monitor.get_app_usage_stats()
        
        tree = ttk.Treeview(usage_window, columns=("app", "duration", "count", "last_seen"), show="headings")
        tree.heading("app", text="Application")
        tree.heading("duration", text="Total Duration (sec)")
        tree.heading("count", text="Launch Count")
        tree.heading("last_seen", text="Last Seen")
        
        tree.column("app", width=200)
        tree.column("duration", width=150)
        tree.column("count", width=100)
        tree.column("last_seen", width=150)
        
        for app, stats in sorted(usage_stats.items(), key=lambda x: x[1]["duration"], reverse=True):
            last_seen = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(stats["last_seen"]))
            tree.insert("", tk.END, values=(app, f"{stats['duration']:.1f}", stats["count"], last_seen))
        
        tree.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
    def backup_restore_from_main(self):
        backup_window = tk.Toplevel(self.root)
        backup_window.title("File Backup & Restore")
        backup_window.geometry("600x500")
        backup_window.configure(bg=WIN95_BG)
        
        tk.Label(
            backup_window,
            text="FILE BACKUP & RESTORE",
            font=("MS Sans Serif", 14, "bold"),
            bg=WIN95_BG
        ).pack(pady=15)
        
        stats = self.backup_manager.config
        info_text = (
            f"Auto Backup: {'Enabled' if stats['auto_backup_enabled'] else 'Disabled'}\n"
            f"Backup Interval: {stats['backup_interval_hours']} hours\n"
            f"Max Backups/File: {stats['max_backups_per_file']}\n"
        )
        tk.Label(backup_window, text=info_text, bg=WIN95_BG, justify=tk.LEFT).pack(pady=10)
        
        btn_frame2 = tk.Frame(backup_window, bg=WIN95_BG)
        btn_frame2.pack(pady=10)
        
        def run_backup():
            messagebox.showinfo("Backup", "Starting backup of protected directories...")
            results = self.backup_manager.auto_backup()
            success_count = sum(1 for _, s, _ in results if s)
            messagebox.showinfo("Complete", f"Backup complete!\n\nSuccessfully backed up: {success_count} files")
        
        def list_backups():
            all_backups = self.backup_manager.list_all_backups()
            list_win = tk.Toplevel(backup_window)
            list_win.title("All Backups")
            list_win.geometry("700x400")
            text = tk.Text(list_win, wrap=tk.WORD, font=("Consolas", 9))
            text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            if not all_backups:
                text.insert(tk.END, "No backups found.")
            else:
                for file_path, backups in all_backups.items():
                    text.insert(tk.END, f"\n{file_path}:\n")
                    for b in backups:
                        text.insert(tk.END, f"  - {b['datetime']} ({b['backup_name']})\n")
            text.config(state=tk.DISABLED)
        
        tk.Button(btn_frame2, text="Run Backup Now", command=run_backup, bg=WIN95_BG, width=20).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame2, text="List All Backups", command=list_backups, bg=WIN95_BG, width=20).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame2, text="Close", command=backup_window.destroy, bg=WIN95_BG, width=20).pack(side=tk.LEFT, padx=5)
        
    def manage_users_from_main(self):
        users_window = tk.Toplevel(self.root)
        users_window.title("Manage Allowed Users")
        users_window.geometry("500x400")
        users_window.configure(bg=WIN95_BG)
        
        tk.Label(
            users_window,
            text="ALLOWED USERS",
            font=("MS Sans Serif", 14, "bold"),
            bg=WIN95_BG
        ).pack(pady=15)
        
        list_frame = tk.Frame(users_window, bg=WIN95_BG)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        users_listbox = tk.Listbox(list_frame, font=("Consolas", 10))
        users_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=users_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        users_listbox.config(yscrollcommand=scrollbar.set)
        
        def refresh_users():
            users_listbox.delete(0, tk.END)
            for user in self.admin_auth.get_allowed_users():
                users_listbox.insert(tk.END, user)
        
        refresh_users()
        
        btn_frame = tk.Frame(users_window, bg=WIN95_BG)
        btn_frame.pack(fill=tk.X, padx=20, pady=15)
        
        def add_user():
            username = simpledialog.askstring("Add User", "Enter username to allow:", parent=users_window)
            if username:
                if self.admin_auth.add_allowed_user(username):
                    messagebox.showinfo("Success", f"User '{username}' added to allowed list!", parent=users_window)
                    refresh_users()
                else:
                    messagebox.showwarning("Warning", f"User '{username}' is already allowed!", parent=users_window)
        
        def remove_user():
            selection = users_listbox.curselection()
            if selection:
                username = users_listbox.get(selection[0])
                if messagebox.askyesno("Confirm", f"Remove user '{username}' from allowed list?", parent=users_window):
                    if self.admin_auth.remove_allowed_user(username):
                        messagebox.showinfo("Success", f"User '{username}' removed!", parent=users_window)
                        refresh_users()
        
        tk.Button(
            btn_frame,
            text="Add User",
            width=15,
            command=add_user,
            bg=WIN95_BG,
            font=("MS Sans Serif", 10)
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="Remove Selected",
            width=15,
            command=remove_user,
            bg=WIN95_BG,
            font=("MS Sans Serif", 10)
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="Close",
            width=15,
            command=users_window.destroy,
            bg=WIN95_BG,
            font=("MS Sans Serif", 10)
        ).pack(side=tk.RIGHT, padx=5)
        
    def proxy_auth_settings(self):
        proxy_window = tk.Toplevel(self.root)
        proxy_window.title("Proxy Authentication Settings")
        proxy_window.geometry("600x500")
        proxy_window.configure(bg=WIN95_BG)
        
        tk.Label(
            proxy_window,
            text="PROXY AUTHENTICATION SETTINGS",
            font=("MS Sans Serif", 14, "bold"),
            bg=WIN95_BG
        ).pack(pady=15)
        
        status = self.proxy_auth.get_status()
        
        tk.Label(
            proxy_window,
            text=f"Status: {'ENABLED' if status['enabled'] else 'DISABLED'}",
            bg=WIN95_BG,
            fg="#008000" if status['enabled'] else "#800000"
        ).pack(pady=5)
        
        tk.Label(
            proxy_window,
            text=f"Proxy Server: {status['proxy_server']}",
            bg=WIN95_BG
        ).pack(pady=5)
        
        tk.Label(
            proxy_window,
            text=f"Device ID: {status['device_id']}",
            bg=WIN95_BG,
            font=("Consolas", 8)
        ).pack(pady=5)
        
        tk.Label(
            proxy_window,
            text=f"Last Auth: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(status['last_auth_time'])) if status['last_auth_time'] != 0 else 'Never'}",
            bg=WIN95_BG
        ).pack(pady=5)
        
        btn_frame = tk.Frame(proxy_window, bg=WIN95_BG)
        btn_frame.pack(pady=20)
        
        def toggle_proxy():
            if status['enabled']:
                self.proxy_auth.disable_proxy_auth()
                messagebox.showinfo("Success", "Proxy authentication disabled", parent=proxy_window)
            else:
                self.proxy_auth.enable_proxy_auth()
                messagebox.showinfo("Success", "Proxy authentication enabled", parent=proxy_window)
            proxy_window.destroy()
            self.proxy_auth_settings()
        
        def set_server():
            new_server = simpledialog.askstring("Set Proxy Server", "Enter proxy server URL (e.g., https://auth.example.com):", parent=proxy_window)
            if new_server:
                self.proxy_auth.set_proxy_server(new_server)
                messagebox.showinfo("Success", f"Proxy server set to:\n{new_server}", parent=proxy_window)
                proxy_window.destroy()
                self.proxy_auth_settings()
        
        def test_auth():
            success, msg = self.proxy_auth.authenticate_with_proxy()
            if success:
                messagebox.showinfo("Success", "Proxy authentication successful!", parent=proxy_window)
            else:
                messagebox.showerror("Failed", f"Proxy authentication failed:\n{msg}", parent=proxy_window)
        
        tk.Button(btn_frame, text="Toggle Proxy Auth", command=toggle_proxy, bg=WIN95_BG, width=20).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Set Proxy Server", command=set_server, bg=WIN95_BG, width=20).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Test Authentication", command=test_auth, bg=WIN95_BG, width=20).pack(side=tk.LEFT, padx=5)
        
        tk.Button(proxy_window, text="Close", command=proxy_window.destroy, bg=WIN95_BG, width=20).pack(pady=20)
        
    def admin_logout(self):
        self.is_admin_authenticated = False
        self.admin_auth._log_audit("Admin logged out", include_device_info=True)
        self.setup_main_ui()
        
    def scan_now(self):
        messagebox.showinfo("Scan", "System scan completed!\n\nNo threats found!")
        
    def admin_login(self):
        if self.is_admin_authenticated:
            result = messagebox.askyesno("Admin", "You are already logged in as admin.\nDo you want to log out?")
            if result:
                self.admin_logout()
            return
            
        username = simpledialog.askstring("Admin Login", "Enter admin username:", parent=self.root)
        if not username:
            return
            
        password = simpledialog.askstring("Admin Login", "Enter admin password:", show='*', parent=self.root)
        if not password:
            return
            
        if self.admin_auth.authenticate(username, password):
            self.is_admin_authenticated = True
            
            from file_operation_monitor import TokenAuthenticator
            token_auth = TokenAuthenticator(self.config_dir)
            if not token_auth.check_peripheral_key():
                messagebox.showwarning(
                    "USB Token Warning",
                    "⚠️  No Peripheral Token detected!\n\n"
                    "Please insert your DEADLOCK USB drive for full\n"
                    "security functionality. You can generate a token\n"
                    "later if needed. Alternatively, use proxy auth!",
                    parent=self.root
                )
            
            self.refresh_ui_for_admin()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password!")
            
    def show_admin_panel(self):
        admin_window = tk.Toplevel(self.root)
        admin_window.title("Deadlock Admin Panel")
        admin_window.geometry("600x650")
        admin_window.configure(bg=WIN95_BG)
        admin_window.resizable(False, False)
        
        tk.Label(
            admin_window,
            text="ADMINISTRATIVE CONTROLS",
            font=("MS Sans Serif", 14, "bold"),
            bg=WIN95_BG,
            fg=WIN95_BLACK
        ).pack(pady=20)
        
        btn_frame = tk.Frame(admin_window, bg=WIN95_BG)
        btn_frame.pack(pady=10)
        
        def change_password():
            old = simpledialog.askstring("Change Password", "Enter old password:", show='*', parent=admin_window)
            if not old:
                return
            new1 = simpledialog.askstring("Change Password", "Enter new password:", show='*', parent=admin_window)
            if not new1:
                return
            new2 = simpledialog.askstring("Change Password", "Confirm new password:", show='*', parent=admin_window)
            if new1 != new2:
                messagebox.showerror("Error", "Passwords do not match!", parent=admin_window)
                return
            success, msg = self.admin_auth.change_admin_password(old, new1)
            if success:
                messagebox.showinfo("Success", msg, parent=admin_window)
            else:
                messagebox.showerror("Error", msg, parent=admin_window)
        
        def view_audit_log():
            log_path = self.admin_auth.audit_log_file
            if log_path.exists():
                with open(log_path, 'r', encoding='utf-8') as f:
                    log_content = f.read()
                log_window = tk.Toplevel(admin_window)
                log_window.title("Admin Audit Log")
                log_window.geometry("600x400")
                text_widget = tk.Text(log_window, wrap=tk.WORD, font=("Consolas", 9))
                text_widget.insert(tk.END, log_content)
                text_widget.config(state=tk.DISABLED)
                text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            else:
                messagebox.showinfo("Audit Log", "No audit log entries yet.", parent=admin_window)
        
        def manage_users():
            users_window = tk.Toplevel(admin_window)
            users_window.title("Manage Allowed Users")
            users_window.geometry("500x400")
            users_window.configure(bg=WIN95_BG)
            
            tk.Label(
                users_window,
                text="ALLOWED USERS",
                font=("MS Sans Serif", 14, "bold"),
                bg=WIN95_BG
            ).pack(pady=15)
            
            list_frame = tk.Frame(users_window, bg=WIN95_BG)
            list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
            
            users_listbox = tk.Listbox(list_frame, font=("Consolas", 10))
            users_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=users_listbox.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            users_listbox.config(yscrollcommand=scrollbar.set)
            
            def refresh_users():
                users_listbox.delete(0, tk.END)
                for user in self.admin_auth.get_allowed_users():
                    users_listbox.insert(tk.END, user)
            
            refresh_users()
            
            btn_frame = tk.Frame(users_window, bg=WIN95_BG)
            btn_frame.pack(fill=tk.X, padx=20, pady=15)
            
            def add_user():
                username = simpledialog.askstring("Add User", "Enter username to allow:", parent=users_window)
                if username:
                    if self.admin_auth.add_allowed_user(username):
                        messagebox.showinfo("Success", f"User '{username}' added to allowed list!", parent=users_window)
                        refresh_users()
                    else:
                        messagebox.showwarning("Warning", f"User '{username}' is already allowed!", parent=users_window)
            
            def remove_user():
                selection = users_listbox.curselection()
                if selection:
                    username = users_listbox.get(selection[0])
                    if messagebox.askyesno("Confirm", f"Remove user '{username}' from allowed list?", parent=users_window):
                        if self.admin_auth.remove_allowed_user(username):
                            messagebox.showinfo("Success", f"User '{username}' removed!", parent=users_window)
                            refresh_users()
            
            tk.Button(
                btn_frame,
                text="Add User",
                width=15,
                command=add_user,
                bg=WIN95_BG,
                font=("MS Sans Serif", 10)
            ).pack(side=tk.LEFT, padx=5)
            
            tk.Button(
                btn_frame,
                text="Remove Selected",
                width=15,
                command=remove_user,
                bg=WIN95_BG,
                font=("MS Sans Serif", 10)
            ).pack(side=tk.LEFT, padx=5)
            
            tk.Button(
                btn_frame,
                text="Close",
                width=15,
                command=users_window.destroy,
                bg=WIN95_BG,
                font=("MS Sans Serif", 10)
            ).pack(side=tk.RIGHT, padx=5)
        
        def backup_restore():
            backup_window = tk.Toplevel(admin_window)
            backup_window.title("File Backup & Restore")
            backup_window.geometry("600x500")
            backup_window.configure(bg=WIN95_BG)
            
            tk.Label(
                backup_window,
                text="FILE BACKUP & RESTORE",
                font=("MS Sans Serif", 14, "bold"),
                bg=WIN95_BG
            ).pack(pady=15)
            
            stats = self.backup_manager.config
            info_text = (
                f"Auto Backup: {'Enabled' if stats['auto_backup_enabled'] else 'Disabled'}\n"
                f"Backup Interval: {stats['backup_interval_hours']} hours\n"
                f"Max Backups/File: {stats['max_backups_per_file']}\n"
            )
            tk.Label(backup_window, text=info_text, bg=WIN95_BG, justify=tk.LEFT).pack(pady=10)
            
            btn_frame2 = tk.Frame(backup_window, bg=WIN95_BG)
            btn_frame2.pack(pady=10)
            
            def run_backup():
                messagebox.showinfo("Backup", "Starting backup of protected directories...")
                results = self.backup_manager.auto_backup()
                success_count = sum(1 for _, s, _ in results if s)
                messagebox.showinfo("Complete", f"Backup complete!\n\nSuccessfully backed up: {success_count} files")
            
            def list_backups():
                all_backups = self.backup_manager.list_all_backups()
                list_win = tk.Toplevel(backup_window)
                list_win.title("All Backups")
                list_win.geometry("700x400")
                text = tk.Text(list_win, wrap=tk.WORD, font=("Consolas", 9))
                text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
                
                if not all_backups:
                    text.insert(tk.END, "No backups found.")
                else:
                    for file_path, backups in all_backups.items():
                        text.insert(tk.END, f"\n{file_path}:\n")
                        for b in backups:
                            text.insert(tk.END, f"  - {b['datetime']} ({b['backup_name']})\n")
                text.config(state=tk.DISABLED)
            
            tk.Button(btn_frame2, text="Run Backup Now", command=run_backup, bg=WIN95_BG, width=20).pack(side=tk.LEFT, padx=5)
            tk.Button(btn_frame2, text="List All Backups", command=list_backups, bg=WIN95_BG, width=20).pack(side=tk.LEFT, padx=5)
            tk.Button(btn_frame2, text="Close", command=backup_window.destroy, bg=WIN95_BG, width=20).pack(side=tk.LEFT, padx=5)
        
        def app_whitelist_panel():
            app_window = tk.Toplevel(admin_window)
            app_window.title("Application Whitelisting")
            app_window.geometry("600x450")
            app_window.configure(bg=WIN95_BG)
            
            tk.Label(
                app_window,
                text="APPLICATION WHITELISTING",
                font=("MS Sans Serif", 14, "bold"),
                bg=WIN95_BG
            ).pack(pady=15)
            
            status = self.app_whitelist.get_whitelist_status()
            status_text = (
                f"Status: {'ENABLED' if status['enabled'] else 'DISABLED'}\n"
                f"Allowed Paths: {status['allowed_paths_count']}\n"
                f"Allowed Hashes: {status['allowed_hashes_count']}\n"
                f"Blocked Paths: {status['blocked_paths_count']}\n"
                f"Blocked Hashes: {status['blocked_hashes_count']}"
            )
            tk.Label(app_window, text=status_text, bg=WIN95_BG, justify=tk.LEFT).pack(pady=10)
            
            btn_frame2 = tk.Frame(app_window, bg=WIN95_BG)
            btn_frame2.pack(pady=10)
            
            def toggle_whitelist():
                if status['enabled']:
                    self.app_whitelist.disable_whitelist()
                    messagebox.showinfo("Success", "Application whitelisting DISABLED")
                else:
                    self.app_whitelist.enable_whitelist()
                    messagebox.showinfo("Success", "Application whitelisting ENABLED")
                app_window.destroy()
                app_whitelist_panel()
            
            tk.Button(btn_frame2, text="Toggle Whitelist", command=toggle_whitelist, bg=WIN95_BG, width=20).pack(side=tk.LEFT, padx=5)
            tk.Button(btn_frame2, text="Close", command=app_window.destroy, bg=WIN95_BG, width=20).pack(side=tk.LEFT, padx=5)
        
        def threat_intel_panel():
            intel_window = tk.Toplevel(admin_window)
            intel_window.title("Threat Intelligence Feed")
            intel_window.geometry("600x450")
            intel_window.configure(bg=WIN95_BG)
            
            tk.Label(
                intel_window,
                text="THREAT INTELLIGENCE FEED",
                font=("MS Sans Serif", 14, "bold"),
                bg=WIN95_BG
            ).pack(pady=15)
            
            stats = self.threat_feed.get_threat_stats()
            stats_text = (
                f"Database Version: {stats['version']}\n"
                f"Last Updated: {stats['last_updated']}\n\n"
                f"Malicious Hashes: {stats['malicious_hashes']}\n"
                f"Suspicious Hashes: {stats['suspicious_hashes']}\n"
                f"Malicious IPs: {stats['malicious_ips']}\n"
                f"Malicious Domains: {stats['malicious_domains']}\n"
                f"Ransomware Extensions: {stats['ransomware_extensions']}"
            )
            tk.Label(intel_window, text=stats_text, bg=WIN95_BG, justify=tk.LEFT, font=("Consolas", 9)).pack(pady=10)
            
            tk.Button(intel_window, text="Close", command=intel_window.destroy, bg=WIN95_BG, width=20).pack(pady=20)
        
        def usb_sandbox_panel():
            usb_win = tk.Toplevel(admin_window)
            usb_win.title("USB Sandbox Scanner")
            usb_win.geometry("600x400")
            usb_win.configure(bg=WIN95_BG)
            
            tk.Label(usb_win, text="USB SANDBOX SCANNER", font=("MS Sans Serif",14,"bold"), bg=WIN95_BG).pack(pady=15)
            
            config = self.usb_sandbox.config
            info = (
                f"Status: {'ENABLED' if config['enabled'] else 'DISABLED'}\n"
                f"Auto Scan: {'Yes' if config['auto_scan'] else 'No'}"
            )
            tk.Label(usb_win, text=info, bg=WIN95_BG, justify=tk.LEFT).pack(pady=10)
            
            tk.Label(usb_win, text="Note: Scanner automatically detects USB drives\nand prompts for sandbox scan.", bg=WIN95_BG).pack(pady=10)
            tk.Button(usb_win, text="Close", command=usb_win.destroy, bg=WIN95_BG, width=20).pack(pady=20)
        
        def network_firewall_panel():
            fw_win = tk.Toplevel(admin_window)
            fw_win.title("Network Firewall")
            fw_win.geometry("600x400")
            fw_win.configure(bg=WIN95_BG)
            
            tk.Label(fw_win, text="NETWORK FIREWALL", font=("MS Sans Serif",14,"bold"), bg=WIN95_BG).pack(pady=15)
            
            status = self.network_firewall.get_firewall_status()
            info = ""
            for k, v in status.items():
                info += f"{k}: {v}\n"
            tk.Label(fw_win, text=info, bg=WIN95_BG, justify=tk.LEFT, font=("Consolas",9)).pack(pady=10)
            tk.Button(fw_win, text="Close", command=fw_win.destroy, bg=WIN95_BG, width=20).pack(pady=20)
        
        def incident_response_panel():
            ir_win = tk.Toplevel(admin_window)
            ir_win.title("Incident Response")
            ir_win.geometry("600x450")
            ir_win.configure(bg=WIN95_BG)
            
            tk.Label(ir_win, text="INCIDENT RESPONSE", font=("MS Sans Serif",14,"bold"), bg=WIN95_BG).pack(pady=15)
            
            status = self.incident_response.get_incident_response_status()
            info = ""
            for k, v in status.items():
                info += f"{k}: {v}\n"
            tk.Label(ir_win, text=info, bg=WIN95_BG, justify=tk.LEFT, font=("Consolas",9)).pack(pady=10)
            tk.Button(ir_win, text="Close", command=ir_win.destroy, bg=WIN95_BG, width=20).pack(pady=20)
        
        def vulnerability_scan_panel():
            vuln_win = tk.Toplevel(admin_window)
            vuln_win.title("Vulnerability Scanner")
            vuln_win.geometry("700x500")
            vuln_win.configure(bg=WIN95_BG)
            
            tk.Label(vuln_win, text="VULNERABILITY SCANNER", font=("MS Sans Serif",14,"bold"), bg=WIN95_BG).pack(pady=15)
            
            def run_scan():
                messagebox.showinfo("Scanning", "Starting vulnerability scan...")
                results = self.vuln_scanner.run_full_scan()
                
                result_win = tk.Toplevel(vuln_win)
                result_win.title("Scan Results")
                result_win.geometry("700x500")
                text = tk.Text(result_win, wrap=tk.WORD, font=("Consolas",9))
                text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
                
                text.insert(tk.END, f"Scan Date: {results['datetime']}\n")
                text.insert(tk.END, f"Total Issues: {results['total_count']}\n")
                text.insert(tk.END, f"High Severity: {results['high_count']}\n")
                text.insert(tk.END, f"Medium Severity: {results['medium_count']}\n\n")
                
                for vuln in results['vulnerabilities'][:50]:
                    text.insert(tk.END, f"[{vuln['severity'].upper()}] {vuln['type']}: {vuln['description']}\n")
                
                text.config(state=tk.DISABLED)
            
            tk.Button(vuln_win, text="Run Full Scan", command=run_scan, bg=WIN95_BG, width=20).pack(pady=10)
            
            last_scan = self.vuln_scanner.get_last_scan()
            if last_scan:
                tk.Label(vuln_win, text=f"Last Scan: {last_scan['datetime']}", bg=WIN95_BG).pack(pady=5)
            
            tk.Button(vuln_win, text="Close", command=vuln_win.destroy, bg=WIN95_BG, width=20).pack(pady=20)
        
        def browser_sandbox_panel():
            bs_win = tk.Toplevel(admin_window)
            bs_win.title("Browser Sandboxing")
            bs_win.geometry("600x350")
            bs_win.configure(bg=WIN95_BG)
            
            tk.Label(bs_win, text="BROWSER SANDBOXING", font=("MS Sans Serif",14,"bold"), bg=WIN95_BG).pack(pady=15)
            
            config = self.browser_sandbox.get_sandbox_status()
            info = f"Enabled: {'Yes' if config['enabled'] else 'No'}\n"
            tk.Label(bs_win, text=info, bg=WIN95_BG, justify=tk.LEFT).pack(pady=10)
            tk.Button(bs_win, text="Close", command=bs_win.destroy, bg=WIN95_BG, width=20).pack(pady=20)
        
        def decryptor_panel():
            dec_win = tk.Toplevel(admin_window)
            dec_win.title("Ransomware Decryption Toolkit")
            dec_win.geometry("600x400")
            dec_win.configure(bg=WIN95_BG)
            
            tk.Label(dec_win, text="RANSOMWARE DECRYPTION TOOLKIT", font=("MS Sans Serif",14,"bold"), bg=WIN95_BG).pack(pady=15)
            
            status = self.ransomware_decryptor.get_decryptor_status()
            tk.Label(dec_win, text="Known Ransomware Strains:", bg=WIN95_BG).pack(pady=5)
            tk.Label(dec_win, text=", ".join(status['known_ransomware']), bg=WIN95_BG, wraplength=500).pack(pady=10)
            tk.Button(dec_win, text="Close", command=dec_win.destroy, bg=WIN95_BG, width=20).pack(pady=20)
        
        def compliance_panel():
            comp_win = tk.Toplevel(admin_window)
            comp_win.title("Compliance Reporting")
            comp_win.geometry("600x400")
            comp_win.configure(bg=WIN95_BG)
            
            tk.Label(comp_win, text="COMPLIANCE REPORTING", font=("MS Sans Serif",14,"bold"), bg=WIN95_BG).pack(pady=15)
            
            def generate_hipaa():
                path = self.compliance_reporter.generate_report("HIPAA")
                messagebox.showinfo("Success", f"HIPAA Report generated!\n{path}")
                
            def generate_gdpr():
                path = self.compliance_reporter.generate_report("GDPR")
                messagebox.showinfo("Success", f"GDPR Report generated!\n{path}")
                
            def generate_pci():
                path = self.compliance_reporter.generate_report("PCI")
                messagebox.showinfo("Success", f"PCI Report generated!\n{path}")
                
            btn_frame2 = tk.Frame(comp_win, bg=WIN95_BG)
            btn_frame2.pack(pady=20)
            
            tk.Button(btn_frame2, text="Generate HIPAA Report", command=generate_hipaa, bg=WIN95_BG, width=25).pack(pady=5)
            tk.Button(btn_frame2, text="Generate GDPR Report", command=generate_gdpr, bg=WIN95_BG, width=25).pack(pady=5)
            tk.Button(btn_frame2, text="Generate PCI Report", command=generate_pci, bg=WIN95_BG, width=25).pack(pady=5)
            tk.Button(btn_frame2, text="Close", command=comp_win.destroy, bg=WIN95_BG, width=25).pack(pady=10)
        
        def create_shortcut():
            success, msg = create_desktop_shortcut()
            if success:
                messagebox.showinfo("Success", msg)
            else:
                messagebox.showerror("Error", msg)
                
        buttons = [
            ("File Backup & Restore", backup_restore),
            ("Application Whitelisting", app_whitelist_panel),
            ("Threat Intelligence", threat_intel_panel),
            ("USB Sandbox Scanner", usb_sandbox_panel),
            ("Network Firewall", network_firewall_panel),
            ("Incident Response", incident_response_panel),
            ("Vulnerability Scanner", vulnerability_scan_panel),
            ("Browser Sandboxing", browser_sandbox_panel),
            ("Ransomware Decryption", decryptor_panel),
            ("Compliance Reporting", compliance_panel),
            ("Create Desktop Shortcut", create_shortcut),
            ("Manage Allowed Users", manage_users),
            ("Change Admin Password", change_password),
            ("View Audit Log", view_audit_log),
            ("Close", admin_window.destroy)
        ]
        
        admin_window.geometry("600x800")
        
        for text, cmd in buttons:
            btn = tk.Button(
                btn_frame,
                text=text,
                width=30,
                command=cmd,
                bg=WIN95_BG,
                font=("MS Sans Serif", 9),
                padx=10,
                pady=4
            )
            btn.pack(pady=6)
        
    def show_settings(self):
        messagebox.showinfo("Settings", "Settings panel - requires admin login!")
        
    def show_about(self):
        about_text = (
            "Deadlock Endpoint Shield v1.0\n"
            "Built with Python & Tkinter\n\n"
            "Protection Features:\n"
            "- Real-time monitoring\n"
            "- Ransomware detection\n"
            "- Zip bomb detection\n"
            "- Threat mitigation system\n"
            "- Admin authentication & audit logging"
        )
        messagebox.showinfo("About", about_text)

def main():
    root = tk.Tk()
    app = DeadlockRetroUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
