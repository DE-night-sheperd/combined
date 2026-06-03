import os
import sys
import time
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext, simpledialog
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from file_access_control import FileAccessController, FileAccessRule, FileAccessMonitor
from file_operation_monitor import FileOperationMonitor, TokenAuthenticator

class FileAccessManagerUI:
    def __init__(self, root):
        self.root = root
        self.root.title("DEADBOLT - FILE ACCESS CONTROL MANAGER")
        self.root.geometry("1200x800")
        self.root.configure(bg="#1a1a2e")
        
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
        header = tk.Frame(self.root, bg="#0f3460", height=80)
        header.pack(fill=tk.X)
        
        tk.Label(
            header,
            text="🔒 DEADBOLT - FILE ACCESS CONTROL",
            font=("Consolas", 24, "bold"),
            bg="#0f3460",
            fg="#00ff00"
        ).pack(pady=20)
        
        main_panes = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, bg="#1a1a2e")
        main_panes.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        left_pane = tk.Frame(main_panes, bg="#1a1a2e")
        main_panes.add(left_pane, minsize=500)
        
        right_pane = tk.Frame(main_panes, bg="#1a1a2e")
        main_panes.add(right_pane, minsize=500)
        
        self.setup_rules_section(left_pane)
        self.setup_logs_section(right_pane)
        
    def setup_rules_section(self, parent):
        rules_frame = tk.LabelFrame(
            parent,
            text="ACCESS RULES",
            bg="#1a1a2e",
            fg="#00ff00",
            font=("Consolas", 14, "bold"),
            padx=10,
            pady=10
        )
        rules_frame.pack(fill=tk.BOTH, expand=True)
        
        btn_frame = tk.Frame(rules_frame, bg="#1a1a2e")
        btn_frame.pack(fill=tk.X, pady=5)
        
        tk.Button(
            btn_frame,
            text="➕ ADD RULE",
            command=self.show_add_rule_dialog,
            bg="#00aa00",
            fg="#ffffff",
            font=("Consolas", 10, "bold"),
            padx=15,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="🗑️ REMOVE SELECTED",
            command=self.remove_selected_rule,
            bg="#aa0000",
            fg="#ffffff",
            font=("Consolas", 10, "bold"),
            padx=15,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="🔄 REFRESH",
            command=self.refresh_rules_list,
            bg="#0088aa",
            fg="#ffffff",
            font=("Consolas", 10, "bold"),
            padx=15,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="▶️ START MONITOR",
            command=self.start_monitor,
            bg="#00aa00",
            fg="#ffffff",
            font=("Consolas", 10, "bold"),
            padx=15,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="⏹️ STOP MONITOR",
            command=self.stop_monitor,
            bg="#aa0000",
            fg="#ffffff",
            font=("Consolas", 10, "bold"),
            padx=15,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="🔑 CHANGE TOKEN",
            command=self.change_token,
            bg="#5500aa",
            fg="#ffffff",
            font=("Consolas", 10, "bold"),
            padx=15,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
        
        columns = ("path", "type", "enabled", "description")
        self.rules_tree = ttk.Treeview(rules_frame, columns=columns, show="headings")
        
        self.rules_tree.heading("path", text="Path")
        self.rules_tree.heading("type", text="Rule Type")
        self.rules_tree.heading("enabled", text="Enabled")
        self.rules_tree.heading("description", text="Description")
        
        self.rules_tree.column("path", width=250)
        self.rules_tree.column("type", width=120)
        self.rules_tree.column("enabled", width=80)
        self.rules_tree.column("description", width=200)
        
        self.rules_tree.pack(fill=tk.BOTH, expand=True, pady=5)
        
        scrollbar = ttk.Scrollbar(rules_frame, orient=tk.VERTICAL, command=self.rules_tree.yview)
        self.rules_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def setup_logs_section(self, parent):
        logs_frame = tk.LabelFrame(
            parent,
            text="ACCESS LOGS",
            bg="#1a1a2e",
            fg="#00ffff",
            font=("Consolas", 14, "bold"),
            padx=10,
            pady=10
        )
        logs_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Button(
            logs_frame,
            text="🔄 REFRESH LOGS",
            command=self.refresh_logs_list,
            bg="#5500aa",
            fg="#ffffff",
            font=("Consolas", 10, "bold"),
            padx=15,
            pady=5
        ).pack(anchor=tk.W, pady=5)
        
        self.logs_text = scrolledtext.ScrolledText(
            logs_frame,
            bg="#000000",
            fg="#00ff00",
            font=("Consolas", 9),
            insertbackground="#00ff00"
        )
        self.logs_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
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
            status = "🔴 BLOCKED" if log["blocked"] else "🟢 ALLOWED"
            self.logs_text.insert(tk.END, f"[{timestamp}] {status} | {log['operation']} | {log['path']}\n")
            
    def show_first_launch_wizard(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("DEADBOLT - FIRST TIME SETUP")
        dialog.geometry("650x550")
        dialog.configure(bg="#1a1a2e")
        dialog.attributes('-topmost', True)
        dialog.grab_set()
        dialog.transient(self.root)
        
        header = tk.Frame(dialog, bg="#00aa00", height=100)
        header.pack(fill=tk.X)
        
        tk.Label(
            header,
            text="🎉 WELCOME TO DEADBOLT!",
            font=("Consolas", 22, "bold"),
            bg="#00aa00",
            fg="#ffffff"
        ).pack(pady=30)
        
        main_frame = tk.Frame(dialog, bg="#1a1a2e", padx=30, pady=30)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(
            main_frame,
            text="This is your first time using Deadbolt.\nPlease set a strong Level 1 Token Key to protect your files!",
            font=("Consolas", 12),
            bg="#1a1a2e",
            fg="#ffffff",
            justify=tk.CENTER
        ).pack(pady=(0, 20))
        
        tk.Label(
            main_frame,
            text="Password Requirements:",
            font=("Consolas", 11, "bold"),
            bg="#1a1a2e",
            fg="#ffff00"
        ).pack(anchor=tk.W)
        
        reqs_frame = tk.Frame(main_frame, bg="#0f3460", padx=20, pady=15)
        reqs_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(reqs_frame, text="• Minimum 8 characters long", bg="#0f3460", fg="#ffffff", font=("Consolas", 10)).pack(anchor=tk.W)
        tk.Label(reqs_frame, text="• At least one uppercase letter", bg="#0f3460", fg="#ffffff", font=("Consolas", 10)).pack(anchor=tk.W)
        tk.Label(reqs_frame, text="• At least one lowercase letter", bg="#0f3460", fg="#ffffff", font=("Consolas", 10)).pack(anchor=tk.W)
        tk.Label(reqs_frame, text="• At least one digit", bg="#0f3460", fg="#ffffff", font=("Consolas", 10)).pack(anchor=tk.W)
        
        tk.Label(
            main_frame,
            text="Enter New Token Key:",
            font=("Consolas", 11, "bold"),
            bg="#1a1a2e",
            fg="#00ffff"
        ).pack(anchor=tk.W, pady=(20, 5))
        
        token1_var = tk.StringVar()
        token1_entry = tk.Entry(main_frame, textvariable=token1_var, font=("Consolas", 14), show="*", width=35)
        token1_entry.pack(fill=tk.X, pady=5)
        token1_entry.focus()
        
        tk.Label(
            main_frame,
            text="Confirm Token Key:",
            font=("Consolas", 11, "bold"),
            bg="#1a1a2e",
            fg="#00ffff"
        ).pack(anchor=tk.W, pady=(15, 5))
        
        token2_var = tk.StringVar()
        tk.Entry(main_frame, textvariable=token2_var, font=("Consolas", 14), show="*", width=35).pack(fill=tk.X, pady=5)
        
        btn_frame = tk.Frame(main_frame, bg="#1a1a2e")
        btn_frame.pack(fill=tk.X, pady=25)
        
        def complete_setup():
            token1 = token1_var.get()
            token2 = token2_var.get()
            
            if token1 != token2:
                messagebox.showerror("Error", "Token keys do not match!", parent=dialog)
                return
                
            try:
                self.authenticator.set_token(token1)
                self.authenticator.mark_first_launch_complete()
                messagebox.showinfo("Success", "Token key set successfully!\nWelcome to Deadbolt!", parent=dialog)
                dialog.destroy()
            except ValueError as e:
                messagebox.showerror("Weak Password", str(e), parent=dialog)
                
        tk.Button(
            btn_frame,
            text="✅ COMPLETE SETUP",
            command=complete_setup,
            bg="#00aa00",
            fg="#ffffff",
            font=("Consolas", 14, "bold"),
            height=2,
            width=25
        ).pack()
            
    def show_add_rule_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Access Rule")
        dialog.geometry("600x450")
        dialog.configure(bg="#1a1a2e")
        
        tk.Label(
            dialog,
            text="ADD NEW ACCESS RULE",
            font=("Consolas", 16, "bold"),
            bg="#1a1a2e",
            fg="#00ff00"
        ).pack(pady=20)
        
        form_frame = tk.Frame(dialog, bg="#1a1a2e")
        form_frame.pack(pady=10, padx=20, fill=tk.X)
        
        tk.Label(form_frame, text="Path:", bg="#1a1a2e", fg="#ffffff", font=("Consolas", 10)).pack(anchor=tk.W)
        path_frame = tk.Frame(form_frame, bg="#1a1a2e")
        path_frame.pack(fill=tk.X, pady=5)
        path_var = tk.StringVar()
        path_entry = tk.Entry(path_frame, textvariable=path_var, font=("Consolas", 10), width=50)
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        def browse_path():
            selected = filedialog.askdirectory(title="Select Folder")
            if selected:
                path_var.set(selected)
        
        tk.Button(
            path_frame,
            text="Browse...",
            command=browse_path,
            bg="#0088aa",
            fg="#ffffff",
            font=("Consolas", 9)
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Label(form_frame, text="Rule Type:", bg="#1a1a2e", fg="#ffffff", font=("Consolas", 10)).pack(anchor=tk.W, pady=(10, 0))
        type_var = tk.StringVar(value="block_access")
        type_options = [
            ("Block All Access", "block_access"),
            ("Block Read", "block_read"),
            ("Block Write", "block_write"),
            ("Block Delete", "block_delete"),
            ("Block Rename", "block_rename")
        ]
        for text, val in type_options:
            tk.Radiobutton(
                form_frame,
                text=text,
                variable=type_var,
                value=val,
                bg="#1a1a2e",
                fg="#ffffff",
                font=("Consolas", 9),
                selectcolor="#0f3460",
                activebackground="#1a1a2e"
            ).pack(anchor=tk.W)
        
        tk.Label(form_frame, text="Description:", bg="#1a1a2e", fg="#ffffff", font=("Consolas", 10)).pack(anchor=tk.W, pady=(10, 0))
        desc_var = tk.StringVar()
        desc_entry = tk.Entry(form_frame, textvariable=desc_var, font=("Consolas", 10), width=60)
        desc_entry.pack(fill=tk.X, pady=5)
        
        enabled_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            form_frame,
            text="Enable Rule Immediately",
            variable=enabled_var,
            bg="#1a1a2e",
            fg="#00ff00",
            font=("Consolas", 10, "bold"),
            selectcolor="#0f3460",
            activebackground="#1a1a2e"
        ).pack(anchor=tk.W, pady=10)
        
        btn_frame = tk.Frame(dialog, bg="#1a1a2e")
        btn_frame.pack(pady=20)
        
        def save_rule():
            path = path_var.get().strip()
            if not path:
                messagebox.showwarning("Warning", "Please select a path!")
                return
            rule = FileAccessRule(
                path=path,
                rule_type=type_var.get(),
                enabled=enabled_var.get(),
                description=desc_var.get()
            )
            self.controller.add_rule(rule)
            self.refresh_rules_list()
            dialog.destroy()
            messagebox.showinfo("Success", "Rule added successfully!")
        
        tk.Button(
            btn_frame,
            text="SAVE RULE",
            command=save_rule,
            bg="#00aa00",
            fg="#ffffff",
            font=("Consolas", 12, "bold"),
            padx=30,
            pady=10
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="CANCEL",
            command=dialog.destroy,
            bg="#555555",
            fg="#ffffff",
            font=("Consolas", 12, "bold"),
            padx=30,
            pady=10
        ).pack(side=tk.LEFT, padx=5)
        
    def remove_selected_rule(self):
        selected = self.rules_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a rule to remove!")
            return
        
        if messagebox.askyesno("Confirm", "Are you sure you want to remove the selected rule?"):
            item = selected[0]
            index = self.rules_tree.index(item)
            self.controller.remove_rule(index)
            self.refresh_rules_list()
            messagebox.showinfo("Success", "Rule removed successfully!")
            
    def start_monitor(self):
        try:
            self.operation_monitor.start()
            messagebox.showinfo("Success", "File operation monitor started!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start monitor: {e}")
            
    def stop_monitor(self):
        try:
            self.operation_monitor.stop()
            messagebox.showinfo("Success", "File operation monitor stopped!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to stop monitor: {e}")
            
    def change_token(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Change Level 1 Token Key")
        dialog.geometry("550x400")
        dialog.configure(bg="#1a1a2e")
        dialog.attributes('-topmost', True)
        dialog.grab_set()
        
        tk.Label(
            dialog,
            text="CHANGE LEVEL 1 TOKEN KEY",
            font=("Consolas", 18, "bold"),
            bg="#1a1a2e",
            fg="#00ff00"
        ).pack(pady=20)
        
        main_frame = tk.Frame(dialog, bg="#1a1a2e", padx=30, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(
            main_frame,
            text="Enter Current Token:",
            font=("Consolas", 11, "bold"),
            bg="#1a1a2e",
            fg="#ffff00"
        ).pack(anchor=tk.W)
        
        current_var = tk.StringVar()
        tk.Entry(main_frame, textvariable=current_var, font=("Consolas", 12), show="*", width=40).pack(fill=tk.X, pady=5)
        
        tk.Label(
            main_frame,
            text="Enter New Token:",
            font=("Consolas", 11, "bold"),
            bg="#1a1a2e",
            fg="#00ffff"
        ).pack(anchor=tk.W, pady=(15, 5))
        
        new_var = tk.StringVar()
        tk.Entry(main_frame, textvariable=new_var, font=("Consolas", 12), show="*", width=40).pack(fill=tk.X, pady=5)
        
        tk.Label(
            main_frame,
            text="Confirm New Token:",
            font=("Consolas", 11, "bold"),
            bg="#1a1a2e",
            fg="#00ffff"
        ).pack(anchor=tk.W, pady=(15, 5))
        
        confirm_var = tk.StringVar()
        tk.Entry(main_frame, textvariable=confirm_var, font=("Consolas", 12), show="*", width=40).pack(fill=tk.X, pady=5)
        
        btn_frame = tk.Frame(main_frame, bg="#1a1a2e")
        btn_frame.pack(pady=20)
        
        def save():
            current = current_var.get()
            new = new_var.get()
            confirm = confirm_var.get()
            
            if not self.authenticator.verify_token(current):
                messagebox.showerror("Error", "Current token is incorrect!", parent=dialog)
                return
                
            if new != confirm:
                messagebox.showerror("Error", "New tokens do not match!", parent=dialog)
                return
                
            try:
                self.authenticator.set_token(new)
                messagebox.showinfo("Success", "Token key updated successfully!", parent=dialog)
                dialog.destroy()
            except ValueError as e:
                messagebox.showerror("Weak Password", str(e), parent=dialog)
                
        tk.Button(
            btn_frame,
            text="✅ UPDATE TOKEN",
            command=save,
            bg="#00aa00",
            fg="#ffffff",
            font=("Consolas", 12, "bold"),
            padx=20,
            pady=10
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="❌ CANCEL",
            command=dialog.destroy,
            bg="#aa0000",
            fg="#ffffff",
            font=("Consolas", 12, "bold"),
            padx=20,
            pady=10
        ).pack(side=tk.LEFT, padx=5)
            
def main():
    root = tk.Tk()
    app = FileAccessManagerUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
