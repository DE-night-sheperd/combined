import os
import sys
import json
import random
import tkinter as tk
from tkinter import messagebox
import win32pipe
import win32file
import pywintypes

PIPE_NAME = r"\\.\pipe\DeadboltIPC"
CONFIG_PATH = os.path.join(os.environ["ProgramData"], "Deadbolt_v1", "config.json")

class DeadboltDaemon:
    def __init__(self):
        self.secret_offset = 1050
        self.load_config()
        
    def load_config(self):
        try:
            if os.path.exists(CONFIG_PATH):
                with open(CONFIG_PATH, "r") as f:
                    config = json.load(f)
                    self.secret_offset = config.get("SecretKeyOffset", 1050)
        except Exception as e:
            print(f"Config load error: {e}")
            
    def show_lockout(self):
        challenge = random.randint(1000, 9999)
        answer = challenge + self.secret_offset
        print(f"Challenge: {challenge}, Answer: {answer}")
        
        root = tk.Tk()
        root.title("Deadbolt Endpoint Shield")
        root.overrideredirect(True)
        root.attributes("-topmost", True)
        root.configure(bg="#000000")
        
        w = root.winfo_screenwidth()
        h = root.winfo_screenheight()
        root.geometry(f"{w}x{h}+0+0")
        
        frame = tk.Frame(root, bg="#000000")
        frame.pack(expand=True, fill=tk.BOTH)
        
        tk.Label(
            frame,
            text="SYSTEM ISOLATED",
            font=("Arial", 72, "bold"),
            fg="#FF0000",
            bg="#000000"
        ).pack(pady=(100, 20))
        
        tk.Label(
            frame,
            text="Unauthorized data access detected. System locked.",
            font=("Arial", 24),
            fg="#FFFFFF",
            bg="#000000"
        ).pack(pady=(0, 50))
        
        cf = tk.Frame(frame, bg="#000000")
        cf.pack(pady=20)
        
        tk.Label(cf, text="CHALLENGE CODE:", font=("Arial", 18, "bold"), fg="#00FF00", bg="#000000").pack(side=tk.LEFT, padx=10)
        tk.Label(cf, text=str(challenge), font=("Arial", 32, "bold"), fg="#00FF00", bg="#000000").pack(side=tk.LEFT, padx=10)
        
        ef = tk.Frame(frame, bg="#000000")
        ef.pack(pady=30)
        
        tk.Label(ef, text="ENTER UNLOCK CODE:", font=("Arial", 18, "bold"), fg="#FFFFFF", bg="#000000").pack(side=tk.LEFT, padx=10)
        
        entry = tk.Entry(ef, font=("Arial", 24, "bold"), width=10, justify=tk.CENTER, bg="#333333", fg="#FFFFFF")
        entry.pack(side=tk.LEFT, padx=10)
        entry.focus_set()
        
        def check(event=None):
            try:
                if int(entry.get()) == answer:
                    root.destroy()
                    print("Unlocked!")
                else:
                    messagebox.showerror("Error", "Wrong code!")
                    entry.delete(0, tk.END)
            except:
                messagebox.showerror("Error", "Enter a number!")
                entry.delete(0, tk.END)
                
        entry.bind("<Return>", check)
        
        tk.Button(frame, text="Unlock (Test)", command=root.destroy, bg="#555555", fg="white", font=("Arial", 14)).pack(pady=30)
        
        root.mainloop()
        
    def start_server(self):
        print("Deadbolt Daemon running...")
        while True:
            try:
                pipe = win32pipe.CreateNamedPipe(
                    PIPE_NAME,
                    win32pipe.PIPE_ACCESS_DUPLEX,
                    win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_READMODE_MESSAGE | win32pipe.PIPE_WAIT,
                    1,
                    65536,
                    65536,
                    0,
                    None
                )
                print("Waiting for alert...")
                
                win32pipe.ConnectNamedPipe(pipe, None)
                data = win32file.ReadFile(pipe, 4096)
                msg = data[1].decode('utf-8')
                print(f"Got: {msg}")
                
                if msg == "BREACH_TRIGGERED":
                    win32file.CloseHandle(pipe)
                    self.show_lockout()
                    break
                
                win32file.CloseHandle(pipe)
            except Exception as e:
                print(f"Error: {e}")
                import time
                time.sleep(1)

def main():
    daemon = DeadboltDaemon()
    daemon.start_server()
    
if __name__ == "__main__":
    main()
