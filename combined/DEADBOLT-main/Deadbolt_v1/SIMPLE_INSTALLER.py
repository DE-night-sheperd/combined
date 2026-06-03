import tkinter as tk
from tkinter import ttk, messagebox

print("Deadbolt Installer starting...")

root = tk.Tk()
root.title("Deadbolt Endpoint Shield - Setup")
root.geometry("650x500")
root.resizable(False, False)

current_step = 0
steps = ["Welcome", "License", "Config", "Install", "Complete"]

def clear_content():
    for widget in content_frame.winfo_children():
        widget.destroy()

def show_step(idx):
    global current_step
    current_step = idx
    
    for i, lbl in enumerate(step_labels):
        if i < idx:
            lbl.config(fg="#ffffff")
        elif i == idx:
            lbl.config(fg="#ffffff", font=("Arial", 9, "bold"))
        else:
            lbl.config(fg="#a0d0f0")
    
    clear_content()
    
    if idx == 0:
        welcome()
    elif idx == 1:
        license_page()
    elif idx == 2:
        config_page()
    elif idx == 3:
        install_page()
    elif idx == 4:
        complete_page()

def welcome():
    tk.Label(
        content_frame,
        text="Welcome to Deadbolt Endpoint Shield Setup",
        font=("Arial", 16, "bold"),
        bg="#ffffff"
    ).pack(pady=(50,30), padx=30, anchor=tk.W)
    
    tk.Label(
        content_frame,
        text="This wizard will guide you through the installation.",
        font=("Arial", 11),
        bg="#ffffff"
    ).pack(pady=10, padx=30, anchor=tk.W)
    
    btn_back.config(state=tk.DISABLED)
    btn_next.config(text="Next >", state=tk.NORMAL)

def license_page():
    tk.Label(
        content_frame,
        text="POPIA License Agreement",
        font=("Arial", 16, "bold"),
        bg="#ffffff"
    ).pack(pady=(30,20), padx=30, anchor=tk.W)
    
    txt = """This software collects personal information for security monitoring only.
By proceeding, you accept the POPIA terms. All data stays local."""
    
    text_box = tk.Text(content_frame, height=10, wrap=tk.WORD, font=("Arial", 10), bg="#f5f5f5", padx=10, pady=10)
    text_box.insert(tk.END, txt)
    text_box.config(state=tk.DISABLED)
    text_box.pack(padx=30, pady=10, fill=tk.BOTH, expand=True)
    
    global agree_var
    agree_var = tk.BooleanVar(value=False)
    
    def toggle_next():
        btn_next.config(state=tk.NORMAL if agree_var.get() else tk.DISABLED)
    
    tk.Checkbutton(
        content_frame,
        text="I accept the agreement",
        variable=agree_var,
        bg="#ffffff",
        font=("Arial", 11),
        command=toggle_next
    ).pack(pady=15, padx=30, anchor=tk.W)
    
    btn_back.config(state=tk.NORMAL)
    btn_next.config(text="Next >", state=tk.DISABLED)

def config_page():
    tk.Label(
        content_frame,
        text="Configuration",
        font=("Arial", 16, "bold"),
        bg="#ffffff"
    ).pack(pady=(30,20), padx=30, anchor=tk.W)
    
    tk.Label(
        content_frame,
        text="Enter secret key offset for unlock:",
        font=("Arial", 11),
        bg="#ffffff"
    ).pack(pady=10, padx=30, anchor=tk.W)
    
    frame = tk.Frame(content_frame, bg="#ffffff")
    frame.pack(pady=20, padx=30, anchor=tk.W)
    
    tk.Label(frame, text="Offset:", font=("Arial", 11, "bold"), bg="#ffffff").pack(side=tk.LEFT)
    
    global offset_entry
    offset_entry = tk.Entry(frame, font=("Arial", 14), width=12, justify=tk.CENTER)
    offset_entry.insert(0, "1050")
    offset_entry.pack(side=tk.LEFT, padx=10)
    
    btn_back.config(state=tk.NORMAL)
    btn_next.config(text="Install", state=tk.NORMAL)

def install_page():
    tk.Label(
        content_frame,
        text="Installing Deadbolt Endpoint Shield...",
        font=("Arial", 16, "bold"),
        bg="#ffffff"
    ).pack(pady=(60,30), padx=30, anchor=tk.W)
    
    global progress
    progress = ttk.Progressbar(content_frame, orient=tk.HORIZONTAL, length=400, mode='determinate')
    progress.pack(pady=20, padx=30)
    
    global status_label
    status_label = tk.Label(content_frame, text="Initializing...", font=("Arial", 11), bg="#ffffff")
    status_label.pack(pady=10, padx=30, anchor=tk.W)
    
    btn_back.config(state=tk.DISABLED)
    btn_next.config(state=tk.DISABLED)
    btn_cancel.config(state=tk.DISABLED)
    
    root.after(100, do_install)

def do_install():
    import time
    steps = ["Creating directories...", "Saving config...", "Copying files...", "Finalizing..."]
    for i, s in enumerate(steps):
        status_label.config(text=s)
        progress['value'] = (i + 1) / len(steps) * 100
        root.update()
        time.sleep(0.7)
    root.after(500, lambda: show_step(4))

def complete_page():
    tk.Label(
        content_frame,
        text="Setup Complete!",
        font=("Arial", 20, "bold"),
        bg="#ffffff"
    ).pack(pady=(60,30), padx=30, anchor=tk.W)
    
    tk.Label(
        content_frame,
        text="Deadbolt Endpoint Shield has been installed successfully!",
        font=("Arial", 12),
        bg="#ffffff"
    ).pack(pady=10, padx=30, anchor=tk.W)
    
    btn_back.config(state=tk.DISABLED)
    btn_next.config(text="Finish", state=tk.NORMAL, command=root.destroy)
    btn_cancel.config(state=tk.DISABLED)

def on_next():
    if current_step < len(steps) - 1:
        show_step(current_step + 1)

def on_back():
    if current_step > 0:
        show_step(current_step - 1)

def on_cancel():
    if messagebox.askyesno("Cancel", "Are you sure you want to cancel?"):
        root.destroy()

main_frame = tk.Frame(root, bg="#ffffff")
main_frame.pack(fill=tk.BOTH, expand=True)

left_panel = tk.Frame(main_frame, bg="#005a9e", width=180)
left_panel.pack(side=tk.LEFT, fill=tk.Y)
left_panel.pack_propagate(False)

tk.Label(
    left_panel,
    text="DEADBOLT\nENDPOINT\nSHIELD",
    font=("Arial", 15, "bold"),
    fg="#ffffff",
    bg="#005a9e"
).pack(pady=40)

step_labels = []
for i, step in enumerate(steps):
    lbl = tk.Label(left_panel, text=step, font=("Arial", 10), fg="#a0d0f0", bg="#005a9e", anchor=tk.W)
    lbl.pack(padx=15, pady=5, fill=tk.X)
    step_labels.append(lbl)

content_frame = tk.Frame(main_frame, bg="#ffffff")
content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

button_frame = tk.Frame(main_frame, bg="#f0f0f0", height=60)
button_frame.pack(side=tk.BOTTOM, fill=tk.X)
button_frame.pack_propagate(False)

btn_cancel = tk.Button(button_frame, text="Cancel", width=10, command=on_cancel, font=("Arial", 10))
btn_cancel.pack(side=tk.RIGHT, padx=15, pady=15)

btn_next = tk.Button(button_frame, text="Next >", width=10, command=on_next, bg="#005a9e", fg="white", font=("Arial", 10))
btn_next.pack(side=tk.RIGHT, padx=5, pady=15)

btn_back = tk.Button(button_frame, text="< Back", width=10, command=on_back, font=("Arial", 10), state=tk.DISABLED)
btn_back.pack(side=tk.RIGHT, padx=5, pady=15)

show_step(0)
root.mainloop()
