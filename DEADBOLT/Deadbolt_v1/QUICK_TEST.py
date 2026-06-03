import tkinter as tk
from tkinter import ttk

print("Showing simple test UI...")

root = tk.Tk()
root.title("Deadbolt - Test")
root.geometry("600x400")
root.configure(bg="#f0f0f0")

tk.Label(
    root,
    text="DEADBOLT ENDPOINT SHIELD",
    font=("Arial", 24, "bold"),
    bg="#f0f0f0"
).pack(pady=40)

tk.Label(
    root,
    text="The wizard is now visible!",
    font=("Arial", 16),
    bg="#f0f0f0"
).pack(pady=20)

tk.Button(
    root,
    text="OK - Close",
    font=("Arial", 14),
    command=root.destroy,
    bg="#005a9e",
    fg="white",
    width=20
).pack(pady=40)

root.mainloop()
