import os
import sys
import time
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext, simpledialog
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from file_access_control import FileAccessController, FileAccessRule, FileAccessMonitor
from file_operation_monitor import FileOperationMonitor, TokenAuthenticator

# Windows 98 Color Palette
WIN98_BG = "#c0c0c0"
WIN98_DARK = "#808080"
WIN98_LIGHT = "#ffffff"
WIN98_BUTTON_FACE = "#c0c0c0"
WIN98_TITLE_BAR = "#000080"
WIN98_TITLE_TEXT = "#ffffff"
WIN98_BLACK = "#000000"

class Win98Button(tk.Button):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs,
                         bg=WIN98_BUTTON_FACE,
                         fg=WIN98_BLACK,
                         activebackground=WIN98_BUTTON_FACE,
                         activeforeground=WIN98_BLACK,
                         relief=tk.RAISED,
                         bd=2,
                         padx=8,
                         pady=4,
                         font=("MS Sans Serif", 8))
        
        self.bind("<Button-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)
        
    def _on_press(self, event):
        self.config(relief=tk.SUNKEN)
        
    def _on_release(self, event):
        self.config(relief=tk.RAISED)
        if self.cget("command"):
            self.cget("command")()

class Win98Frame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs,
                         bg=WIN98_BG,
                         bd=2,
                         relief=tk.SUNKEN)

class Win98LabelFrame(tk.LabelFrame):
    def __init__(self, parent, text, *args, **kwargs):
        super().__init__(parent, text=text, *args, **kwargs,
                         bg=WIN98_BG,
                         fg=WIN98_BLACK,
                         font=("MS Sans Serif", 8, "bold"),
                         bd=2,
                         relief=tk.GROOVE)

class FileAccessManagerUI_Win98:
    def __init__(self, root):
        self.root = root
        self.root.title("Deadbolt - File Access Control")
        self.root.geometry("1000x700")
        self.root.configure(bg=WIN98_BG)
        
        self.controller = FileAccessController()
        self.monitor = FileAccessMonitor(self.controller)
        self.operation_monitor = FileOperationMonitor(self.controller)
        self.authenticator = TokenAuthenticator(Path.home() / ".deadbolt")
        
        self.setup_ui()
        self.refresh_rules_list()
        self.refresh_logs_list()
        
        if self.authenticator.is_first_launch:
            self.root.after(500, self.show_first_launch_wizard)
        
    def setup_ui(self):
        title_bar = tk.Frame(self.root, bg=WIN98_TITLE_BAR, height=30)
        title_bar.pack(fill=tk.X)
        
        tk.Label(
            title_bar,
            text="  Deadbolt - File Access Control Manager",
            font=("MS Sans Serif", 10, "bold"),
            bg=WIN98_TITLE_BAR,
            fg=WIN98_TITLE_TEXT
        ).pack(side=tk.LEFT, pady=5)
        
        main_frame = tk.Frame(self.root, bg=WIN98_BG, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        left_frame = tk.Frame(main_frame, bg=WIN98_BG)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,5))
        
        right_frame = tk.Frame(main_frame, bg=WIN98_BG)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5,0))
        
        self.setup_rules_section(left_frame)
        self.setup_logs_section(right_frame)
        
        btn_frame = tk.Frame(self.root, bg=WIN98_BG, padx=10, pady=10)
        btn_frame.pack(fill=tk.X)
        
        Win98Button(btn_frame, text="▶️ START MONITOR", command=self.start_monitor).pack(side=tk.LEFT, padx=2)
        Win98Button(btn_frame, text="⏹️ STOP MONITOR", command=self.stop_monitor).pack(side=tk.LEFT, padx=2)
        Win98Button(btn_frame, text="🔑 CHANGE TOKEN", command=self.change_token).pack(side=tk.LEFT, padx=2)
        Win98Button(btn_frame, text="❌ EXIT", command=self.root.quit).pack(side=tk.RIGHT, padx=2)
        
    def setup_rules_section(self, parent):
        rules_frame = Win98LabelFrame(parent, "ACCESS RULES")
        rules_frame.pack(fill=tk.BOTH, expand=True)
        
        btn_inner_frame = tk.Frame(rules_frame, bg=WIN98_BG)
        btn_inner_frame.pack(fill=tk.X, padx=5, pady=5)
        
        Win98Button(btn_inner_frame, text="➕ ADD RULE", command=self.show_add_rule_dialog).pack(side=tk.LEFT, padx=2)
        Win98Button(btn_inner_frame, text="🗑️ REMOVE", command=self.remove_selected_rule).pack(side=tk.LEFT, padx=2)
        Win98Button(btn_inner_frame, text="🔄 REFRESH", command=self.refresh_rules_list).pack(side=tk.LEFT, padx=2)
        
        tree_frame = Win98Frame(rules_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0,5))
        
        self.rules_tree = ttk.Treeview(tree_frame, columns=("path", "type", "enabled", "desc"), show="headings", height=15)
        self.rules_tree.heading("path", text="Path")
        self.rules_tree.heading("type", text="Type")
        self.rules_tree.heading("enabled", text="Enabled")
        self.rules_tree.heading("desc", text="Description")
        
        self.rules_tree.column("path", width=200)
        self.rules_tree.column("type", width=100)
        self.rules_tree.column("enabled", width=60)
        self.rules_tree.column("desc", width=150)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.rules_tree.yview)
        self.rules_tree.configure(yscrollcommand=scrollbar.set)
        
        self.rules_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def setup_logs_section(self, parent):
        logs_frame = Win98LabelFrame(parent, "ACCESS LOGS")
        logs_frame.pack(fill=tk.BOTH, expand=True)
        
        text_frame = Win98Frame(logs_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.logs_text = scrolledtext.ScrolledText(
            text_frame,
            font=("MS Sans Serif", 8),
            bg=WIN98_LIGHT,
            fg=WIN98_BLACK,
            wrap=tk.WORD
        )
        self.logs_text.pack(fill=tk.BOTH, expand=True)
        
    def refresh_rules_list(self):
        for item in self.rules_tree.get_children():
            self.rules_tree.delete(item)
        rules = self.controller.get_rules()
        for rule in rules:
            self.rules_tree.insert("", tk.END, values=(
                rule.path,
                rule.rule_type,
                "Yes" if rule.enabled else "No",
                rule.description
            ))
            
    def refresh_logs_list(self):
        self.logs_text.delete(1.0, tk.END)
        logs = self.monitor.get_logs()
        for log in reversed(logs[-100:]):
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(log["timestamp"]))
            status = "BLOCKED" if log["blocked"] else "ALLOWED"
            self.logs_text.insert(tk.END, f"[{timestamp}] {status} | {log['operation']} | {log['path']}\n")
            
    def show_first_launch_wizard(self):
        wizard = tk.Toplevel(self.root)
        wizard.title("Welcome to Deadbolt - Setup")
        wizard.geometry("550x450")
        wizard.configure(bg=WIN98_BG)
        wizard.attributes('-topmost', True)
        wizard.grab_set()
        wizard.transient(self.root)
        
        title_frame = tk.Frame(wizard, bg=WIN98_TITLE_BAR, height=28)
        title_frame.pack(fill=tk.X)
        tk.Label(title_frame, text="  Welcome to Deadbolt", bg=WIN98_TITLE_BAR, fg=WIN98_TITLE_TEXT, font=("MS Sans Serif", 9, "bold")).pack(side=tk.LEFT, pady=5)
        
        main_frame = tk.Frame(wizard, bg=WIN98_BG, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(main_frame, text="This is your first time using Deadbolt.\nPlease set a strong Level 1 Token Key.", bg=WIN98_BG, fg=WIN98_BLACK, font=("MS Sans Serif", 10)).pack(pady=(0,20))
        
        tk.Label(main_frame, text="Password Requirements:", bg=WIN98_BG, fg=WIN98_BLACK, font=("MS Sans Serif", 9, "bold")).pack(anchor=tk.W)
        
        reqs_frame = Win98Frame(main_frame)
        reqs_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(reqs_frame, text="• Minimum 8 characters long", bg=WIN98_BG, fg=WIN98_BLACK, font=("MS Sans Serif", 9)).pack(anchor=tk.W, padx=10, pady=2)
        tk.Label(reqs_frame, text="• At least one uppercase letter", bg=WIN98_BG, fg=WIN98_BLACK, font=("MS Sans Serif", 9)).pack(anchor=tk.W, padx=10, pady=2)
        tk.Label(reqs_frame, text="• At least one lowercase letter", bg=WIN98_BG, fg=WIN98_BLACK, font=("MS Sans Serif", 9)).pack(anchor=tk.W, padx=10, pady=2)
        tk.Label(reqs_frame, text="• At least one digit", bg=WIN98_BG, fg=WIN98_BLACK, font=("MS Sans Serif", 9)).pack(anchor=tk.W, padx=10, pady=2)
        
        tk.Label(main_frame, text="Enter New Token Key:", bg=WIN98_BG, fg=WIN98_BLACK, font=("MS Sans Serif", 9, "bold")).pack(anchor=tk.W, pady=(15,5))
        token1_var = tk.StringVar()
        tk.Entry(main_frame, textvariable=token1_var, font=("MS Sans Serif", 10), show="*", width=40).pack(fill=tk.X, pady=5)
        
        tk.Label(main_frame, text="Confirm Token Key:", bg=WIN98_BG, fg=WIN98_BLACK, font=("MS Sans Serif", 9, "bold")).pack(anchor=tk.W, pady=(15,5))
        token2_var = tk.StringVar()
        tk.Entry(main_frame, textvariable=token2_var, font=("MS Sans Serif", 10), show="*", width=40).pack(fill=tk.X, pady=5)
        
        btn_frame = tk.Frame(main_frame, bg=WIN98_BG)
        btn_frame.pack(fill=tk.X, pady=20)
        
        def complete():
            t1 = token1_var.get()
            t2 = token2_var.get()
            if t1 != t2:
                messagebox.showerror("Error", "Token keys do not match!", parent=wizard)
                return
            try:
                self.authenticator.set_token(t1)
                self.authenticator.mark_first_launch_complete()
                messagebox.showinfo("Success", "Token key set successfully!", parent=wizard)
                wizard.destroy()
            except ValueError as e:
                messagebox.showerror("Weak Password", str(e), parent=wizard)
        
        Win98Button(btn_frame, text="✅ COMPLETE", command=complete).pack()
        
    def show_add_rule_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Access Rule")
        dialog.geometry("550x400")
        dialog.configure(bg=WIN98_BG)
        
        title_frame = tk.Frame(dialog, bg=WIN98_TITLE_BAR, height=28)
        title_frame.pack(fill=tk.X)
        tk.Label(title_frame, text="  Add Access Rule", bg=WIN98_TITLE_BAR, fg=WIN98_TITLE_TEXT, font=("MS Sans Serif", 9, "bold")).pack(side=tk.LEFT, pady=5)
        
        main_frame = tk.Frame(dialog, bg=WIN98_BG, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(main_frame, text="Path:", bg=WIN98_BG, fg=WIN98_BLACK, font=("MS Sans Serif", 9)).pack(anchor=tk.W)
        path_frame = tk.Frame(main_frame, bg=WIN98_BG)
        path_frame.pack(fill=tk.X, pady=5)
        path_var = tk.StringVar()
        path_entry = tk.Entry(path_frame, textvariable=path_var, font=("MS Sans Serif", 9), width=40)
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        def browse():
            p = filedialog.askdirectory(title="Select Folder")
            if p:
                path_var.set(p)
        Win98Button(path_frame, text="Browse...", command=browse).pack(side=tk.LEFT, padx=5)
        
        tk.Label(main_frame, text="Rule Type:", bg=WIN98_BG, fg=WIN98_BLACK, font=("MS Sans Serif", 9)).pack(anchor=tk.W, pady=(10,0))
        type_var = tk.StringVar(value="block_access")
        options = [
            ("Block All Access", "block_access"),
            ("Block Read", "block_read"),
            ("Block Write", "block_write"),
            ("Block Delete", "block_delete"),
            ("Block Rename", "block_rename")
        ]
        for text, val in options:
            tk.Radiobutton(main_frame, text=text, variable=type_var, value=val, bg=WIN98_BG, fg=WIN98_BLACK, font=("MS Sans Serif", 9)).pack(anchor=tk.W)
        
        tk.Label(main_frame, text="Description:", bg=WIN98_BG, fg=WIN98_BLACK, font=("MS Sans Serif", 9)).pack(anchor=tk.W, pady=(10,0))
        desc_var = tk.StringVar()
        tk.Entry(main_frame, textvariable=desc_var, font=("MS Sans Serif", 9), width=50).pack(fill=tk.X, pady=5)
        
        enabled_var = tk.BooleanVar(value=True)
        tk.Checkbutton(main_frame, text="Enable Rule Immediately", variable=enabled_var, bg=WIN98_BG, fg=WIN98_BLACK, font=("MS Sans Serif", 9)).pack(anchor=tk.W, pady=10)
        
        btn_frame = tk.Frame(main_frame, bg=WIN98_BG)
        btn_frame.pack(pady=15)
        
        def save():
            p = path_var.get().strip()
            if not p:
                messagebox.showwarning("Warning", "Please select a path!", parent=dialog)
                return
            rule = FileAccessRule(path=p, rule_type=type_var.get(), enabled=enabled_var.get(), description=desc_var.get())
            self.controller.add_rule(rule)
            self.refresh_rules_list()
            messagebox.showinfo("Success", "Rule added successfully!", parent=dialog)
            dialog.destroy()
        
        Win98Button(btn_frame, text="OK", command=save).pack(side=tk.LEFT, padx=5)
        Win98Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
    def remove_selected_rule(self):
        selected = self.rules_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a rule to remove!", parent=self.root)
            return
        if messagebox.askyesno("Confirm", "Remove selected rule?", parent=self.root):
            idx = self.rules_tree.index(selected[0])
            self.controller.remove_rule(idx)
            self.refresh_rules_list()
            
    def start_monitor(self):
        try:
            self.operation_monitor.start()
            messagebox.showinfo("Success", "Monitor started!", parent=self.root)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start monitor: {e}", parent=self.root)
            
    def stop_monitor(self):
        try:
            self.operation_monitor.stop()
            messagebox.showinfo("Success", "Monitor stopped!", parent=self.root)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to stop monitor: {e}", parent=self.root)
            
    def change_token(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Change Token Key")
        dialog.geometry("500x350")
        dialog.configure(bg=WIN98_BG)
        
        title_frame = tk.Frame(dialog, bg=WIN98_TITLE_BAR, height=28)
        title_frame.pack(fill=tk.X)
        tk.Label(title_frame, text="  Change Token Key", bg=WIN98_TITLE_BAR, fg=WIN98_TITLE_TEXT, font=("MS Sans Serif", 9, "bold")).pack(side=tk.LEFT, pady=5)
        
        main_frame = tk.Frame(dialog, bg=WIN98_BG, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(main_frame, text="Current Token:", bg=WIN98_BG, fg=WIN98_BLACK, font=("MS Sans Serif", 9)).pack(anchor=tk.W)
        curr_var = tk.StringVar()
        tk.Entry(main_frame, textvariable=curr_var, font=("MS Sans Serif", 9), show="*", width=40).pack(fill=tk.X, pady=5)
        
        tk.Label(main_frame, text="New Token:", bg=WIN98_BG, fg=WIN98_BLACK, font=("MS Sans Serif", 9)).pack(anchor=tk.W, pady=(15,5))
        new_var = tk.StringVar()
        tk.Entry(main_frame, textvariable=new_var, font=("MS Sans Serif", 9), show="*", width=40).pack(fill=tk.X, pady=5)
        
        tk.Label(main_frame, text="Confirm New Token:", bg=WIN98_BG, fg=WIN98_BLACK, font=("MS Sans Serif", 9)).pack(anchor=tk.W, pady=(15,5))
        conf_var = tk.StringVar()
        tk.Entry(main_frame, textvariable=conf_var, font=("MS Sans Serif", 9), show="*", width=40).pack(fill=tk.X, pady=5)
        
        btn_frame = tk.Frame(main_frame, bg=WIN98_BG)
        btn_frame.pack(pady=15)
        
        def save():
            if not self.authenticator.verify_token(curr_var.get()):
                messagebox.showerror("Error", "Current token is incorrect!", parent=dialog)
                return
            if new_var.get() != conf_var.get():
                messagebox.showerror("Error", "New tokens do not match!", parent=dialog)
                return
            try:
                self.authenticator.set_token(new_var.get())
                messagebox.showinfo("Success", "Token updated!", parent=dialog)
                dialog.destroy()
            except ValueError as e:
                messagebox.showerror("Weak Password", str(e), parent=dialog)
        
        Win98Button(btn_frame, text="OK", command=save).pack(side=tk.LEFT, padx=5)
        Win98Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

def main():
    root = tk.Tk()
    app = FileAccessManagerUI_Win98(root)
    root.mainloop()

if __name__ == "__main__":
    main()
