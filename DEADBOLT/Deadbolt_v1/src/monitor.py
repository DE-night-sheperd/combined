import os
import time
import threading
import win32pipe
import win32file
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from zip_bomb_detector import ZipBombDetector

TARGET_DIR = r"C:\DeadboltTest"
PIPE_NAME = r"\\.\pipe\DeadboltIPC"
THRESHOLD_MB = 50
WINDOW_SEC = 5

class MonitorHandler(FileSystemEventHandler):
    def __init__(self):
        self.events = []
        self.lock = threading.Lock()
        self.zip_detector = ZipBombDetector()
        
    def on_modified(self, event):
        if not event.is_directory:
            self.track(event.src_path)
            
    def on_created(self, event):
        if not event.is_directory:
            self.track(event.src_path)
            
    def track(self, path):
        try:
            size = os.path.getsize(path)
            now = time.time()
            
            # Check for zip bomb first!
            if self.zip_detector.scan_file(path):
                print(f"⚠️  ZIP BOMB DETECTED: {path}")
                send_alert()
                return
                
            with self.lock:
                self.events.append((size, now))
                self.check(now)
        except:
            pass
            
    def check(self, now):
        cutoff = now - WINDOW_SEC
        total = 0
        new = []
        for s, ts in self.events:
            if ts > cutoff:
                total += s
                new.append((s, ts))
        self.events = new
        if total > THRESHOLD_MB * 1024 * 1024:
            print(f"ALERT: {total} bytes in {WINDOW_SEC} sec!")
            send_alert()

def send_alert():
    try:
        handle = win32file.CreateFile(
            PIPE_NAME,
            win32file.GENERIC_WRITE,
            0,
            None,
            win32file.OPEN_EXISTING,
            0,
            None
        )
        win32file.WriteFile(handle, b"BREACH_TRIGGERED")
        win32file.CloseHandle(handle)
        print("Alert sent!")
        os._exit(0)
    except Exception as e:
        print(f"Failed: {e}")

def main():
    print("Deadbolt Monitor starting...")
    if not os.path.exists(TARGET_DIR):
        os.makedirs(TARGET_DIR)
        print(f"Created: {TARGET_DIR}")
        
    handler = MonitorHandler()
    observer = Observer()
    observer.schedule(handler, path=TARGET_DIR, recursive=False)
    observer.start()
    print(f"Monitoring: {TARGET_DIR}")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    main()
