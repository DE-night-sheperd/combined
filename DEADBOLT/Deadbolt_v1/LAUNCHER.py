import tkinter as tk
import random
import time
import subprocess
import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from file_operation_monitor import TokenAuthenticator

print("DEADLOCK ENDPOINT SHIELD - LAUNCHER")

def check_professional_install():
    appdata_path = os.path.join(os.environ["ProgramData"], "DeadlockEndpointShield")
    config_path = os.path.join(appdata_path, "config.json")
    return os.path.exists(config_path)

def check_first_launch():
    config_dir = Path.home() / ".deadlock"
    config_dir.mkdir(parents=True, exist_ok=True)
    first_launch_file = config_dir / ".first_launch"
    # Explicitly check for the marker file, don't create TokenAuthenticator here!
    return not first_launch_file.exists()

def run_professional_wizard():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    wizard_path = os.path.join(script_dir, "DEADLOCK_PROFESSIONAL_WIZARD.py")
    if os.path.exists(wizard_path):
        subprocess.run([sys.executable, wizard_path])

def run_key_generation_wizard():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    wizard_path = os.path.join(script_dir, "DEADLOCK_INSTALL_WIZARD.py")
    if os.path.exists(wizard_path):
        subprocess.run([sys.executable, wizard_path])

def launch_main_application():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    main_app_path = os.path.join(script_dir, "src", "retro_ui.py")
    if os.path.exists(main_app_path):
        subprocess.Popen([sys.executable, main_app_path])

class PixelLockIntro:
    def __init__(self, root):
        self.root = root
        self.root.title("Deadlock Endpoint Shield")
        self.root.attributes("-fullscreen", True)
        self.root.configure(bg="#000000")
        self.root.overrideredirect(True)
        
        self.screen_w = self.root.winfo_screenwidth()
        self.screen_h = self.root.winfo_screenheight()
        
        self.canvas = tk.Canvas(self.root, width=self.screen_w, height=self.screen_h, bg="#000000", highlightthickness=0)
        self.canvas.pack()
        
        self.pixel_size = 20
        self.cols = self.screen_w // self.pixel_size
        self.rows = self.screen_h // self.pixel_size
        
        self.pixels = []
        self.animation_step = 0
        self.create_pixels()
        self.animate()
        
    def create_pixels(self):
        cx = self.screen_w // 2
        cy = self.screen_h // 2
        
        lock_pattern = [
            "    ########    ",
            "   ##      ##   ",
            "  ##        ##  ",
            " ##          ## ",
            " ##  ######  ## ",
            " ##  #    #  ## ",
            " ##  #    #  ## ",
            " ##  ######  ## ",
            " ##          ## ",
            "  ##        ##  ",
            "   ##      ##   ",
            "    ########    "
        ]
        
        pattern_w = len(lock_pattern[0]) * self.pixel_size
        pattern_h = len(lock_pattern) * self.pixel_size
        start_x = cx - pattern_w // 2
        start_y = cy - pattern_h // 2
        
        for row_idx, row in enumerate(lock_pattern):
            for col_idx, char in enumerate(row):
                if char == '#':
                    x = start_x + col_idx * self.pixel_size
                    y = start_y + row_idx * self.pixel_size
                    
                    start_x_rand = random.randint(-self.screen_w, self.screen_w * 2)
                    start_y_rand = random.randint(-self.screen_h, self.screen_h * 2)
                    
                    rect = self.canvas.create_rectangle(
                        start_x_rand, start_y_rand,
                        start_x_rand + self.pixel_size, start_y_rand + self.pixel_size,
                        fill="#00ff00", outline=""
                    )
                    
                    self.pixels.append({
                        "id": rect,
                        "target_x": x,
                        "target_y": y,
                        "current_x": start_x_rand,
                        "current_y": start_y_rand,
                        "speed": random.uniform(0.03, 0.08)
                    })
        
        title_id = self.canvas.create_text(
            cx, cy + pattern_h//2 + 80,
            text="DEADLOCK\nENDPOINT SHIELD",
            fill="#00ff00",
            font=("Courier New", 36, "bold"),
            justify=tk.CENTER,
            state=tk.HIDDEN
        )
        self.title_obj = title_id
        
    def animate(self):
        all_arrived = True
        for pixel in self.pixels:
            dx = pixel["target_x"] - pixel["current_x"]
            dy = pixel["target_y"] - pixel["current_y"]
            
            if abs(dx) > 1 or abs(dy) > 1:
                all_arrived = False
                pixel["current_x"] += dx * pixel["speed"]
                pixel["current_y"] += dy * pixel["speed"]
                
                self.canvas.coords(
                    pixel["id"],
                    pixel["current_x"], pixel["current_y"],
                    pixel["current_x"] + self.pixel_size, pixel["current_y"] + self.pixel_size
                )
        
        if all_arrived:
            self.animation_step += 1
            if self.animation_step == 1:
                self.canvas.itemconfig(self.title_obj, state=tk.NORMAL)
                self.root.after(1500, self.finish)
            else:
                self.root.after(50, self.animate)
        else:
            self.root.after(30, self.animate)
            
    def finish(self):
        self.root.destroy()
        proceed_with_setup()
        
def proceed_with_setup():
    # FOR TESTING: ALWAYS RUN BOTH WIZARDS!
    print("=== TEST MODE: RUNNING ALL WIZARDS ===")
    run_professional_wizard()
    run_key_generation_wizard()
    
    launch_main_application()

def main():
    root = tk.Tk()
    app = PixelLockIntro(root)
    root.mainloop()

if __name__ == "__main__":
    main()
