import os
import time
import threading
from collections import deque
from pathlib import Path

# Ransomware detection configuration
KNOWN_RANSOMWARE_EXTENSIONS = [
    '.locky', '.zepto', '.odin', '.zzzzz', '.xyz', '.abc', '.aaa',
    '.crypt', '.crypto', '.cryptowall', '.onion', '.tor', '.ctbl',
    '.bart', '.wnry', '.wcry', '.petya', '.goldeneye', '.kraken',
    '.cerber', '.locky', '.teslacrypt', '.cryptxxx', '.raas', '.hydra',
    '.7z.encrypted', '.encrypted', '.enc', '.ecc', '.exx', '.zzz',
    '.micro', '.diablo6', '.lethic', '.rap', '.karl', '.danabot', '.glock'
]

# Common ransomware file patterns
ENCRYPTION_INDICATORS = [
    'README.txt', 'README.html', 'README.hta', 'DECRYPT.txt',
    'INSTRUCTIONS.txt', 'RECOVERY.txt', 'HOW_TO_DECRYPT.txt',
    'HELP_DECRYPT.txt', 'RECOVERY_FILES.txt', 'DECRYPT_INSTRUCTIONS.txt'
]

# Monitoring thresholds
FILE_MODIFICATION_THRESHOLD = 20  # Files per second
ENCRYPTED_EXTENSION_THRESHOLD = 5  # Suspicious extensions in 10 seconds


class RansomwareDetector:
    def __init__(self):
        self.lock = threading.Lock()
        self.file_events = deque(maxlen=1000)
        self.suspicious_extensions = deque(maxlen=100)
        self.start_time = time.time()
        
    def track_file_event(self, file_path, event_type='modified'):
        """Track file system events for ransomware patterns"""
        now = time.time()
        file_ext = Path(file_path).suffix.lower()
        file_name = Path(file_path).name.lower()
        
        with self.lock:
            self.file_events.append((now, file_path, event_type, file_ext))
            
            # Check 1: Known ransomware extension
            if file_ext in KNOWN_RANSOMWARE_EXTENSIONS:
                print(f"⚠️  RANSOMWARE INDICATOR: Suspicious extension {file_ext} - {file_path}")
                self.suspicious_extensions.append((now, file_path))
                return True
                
            # Check 2: Ransomware note file
            if any(indicator.lower() in file_name for indicator in ENCRYPTION_INDICATORS):
                print(f"⚠️  RANSOMWARE INDICATOR: Possible ransom note - {file_path}")
                return True
                
        return False
        
    def check_high_volume_modifications(self):
        """Check for rapid file modifications (ransomware encryption pattern)"""
        now = time.time()
        one_second_ago = now - 1
        
        with self.lock:
            recent_events = [e for e in self.file_events if e[0] > one_second_ago]
            
        if len(recent_events) > FILE_MODIFICATION_THRESHOLD:
            print(f"⚠️  RANSOMWARE INDICATOR: High file modification volume - {len(recent_events)} files/sec!")
            return True
            
        return False
        
    def check_suspicious_extension_spike(self):
        """Check for many suspicious extensions appearing quickly"""
        now = time.time()
        ten_seconds_ago = now - 10
        
        with self.lock:
            recent_suspicious = [e for e in self.suspicious_extensions if e[0] > ten_seconds_ago]
            
        if len(recent_suspicious) > ENCRYPTED_EXTENSION_THRESHOLD:
            print(f"⚠️  RANSOMWARE INDICATOR: {len(recent_suspicious)} suspicious extensions in 10 sec!")
            return True
            
        return False
        
    def scan_file_for_encryption(self, file_path):
        """Simple heuristic scan for encrypted file patterns"""
        try:
            if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
                return False
                
            # Check for high entropy (encrypted files have random data = high entropy)
            with open(file_path, 'rb') as f:
                data = f.read(min(4096, os.path.getsize(file_path)))
                
            if len(data) < 256:
                return False
                
            # Calculate byte frequency
            byte_counts = [0] * 256
            for byte in data:
                byte_counts[byte] += 1
                
            # Calculate entropy
            entropy = 0
            for count in byte_counts:
                if count > 0:
                    p = count / len(data)
                    entropy -= p * (p.bit_length() - 1)  # Approximate
                    
            # High entropy = possible encryption
            if entropy > 7.5:  # Close to maximum 8 bits
                print(f"⚠️  RANSOMWARE INDICATOR: High entropy (possible encryption) - {file_path}")
                return True
                
        except Exception:
            pass
            
        return False
        
    def is_ransomware_activity_detected(self):
        """Check all ransomware indicators"""
        if self.check_high_volume_modifications():
            return True
        if self.check_suspicious_extension_spike():
            return True
        return False


# Example usage
if __name__ == "__main__":
    print("=" * 60)
    print("DEADBOLT RANSOMWARE DETECTOR")
    print("=" * 60)
    
    detector = RansomwareDetector()
    
    # Test with common extensions
    test_extensions = ['.txt', '.docx', '.locky', '.encrypted']
    
    print("\nTesting ransomware detection...\n")
    
    for ext in test_extensions:
        test_file = f"test_file{ext}"
        detector.track_file_event(test_file, 'created')
        
    print("\n✅ Ransomware detector module loaded!")
