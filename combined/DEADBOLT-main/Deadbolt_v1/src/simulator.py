import os
import threading
import time

TARGET_DIR = r"C:\DeadboltTest"
NUM_FILES = 100
FILE_SIZE = 1024 * 1024
NUM_THREADS = 10

def generate():
    print("Generating test files...")
    os.makedirs(TARGET_DIR, exist_ok=True)
    for i in range(NUM_FILES):
        path = os.path.join(TARGET_DIR, f"test_{i}.dat")
        with open(path, "wb") as f:
            f.write(bytes([i % 256]) * FILE_SIZE)
    print(f"Generated {NUM_FILES} files")

def read_files(file_list, thread_id):
    for path in file_list:
        start = time.time()
        with open(path, "rb") as f:
            data = f.read()
        print(f"[Thread {thread_id}] Read {os.path.basename(path)} ({len(data)} bytes)")

def attack():
    print("\nStarting attack simulation...")
    all_files = []
    for f in os.listdir(TARGET_DIR):
        path = os.path.join(TARGET_DIR, f)
        if os.path.isfile(path):
            all_files.append(path)
            
    chunk = (len(all_files) + NUM_THREADS - 1) // NUM_THREADS
    threads = []
    
    for i in range(NUM_THREADS):
        s = i * chunk
        e = min(s + chunk, len(all_files))
        t = threading.Thread(target=read_files, args=(all_files[s:e], i))
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()
    print("\nAttack complete!")

def main():
    print("Deadbolt Attack Simulator")
    generate()
    time.sleep(1)
    attack()

if __name__ == "__main__":
    main()
