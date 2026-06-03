import os
import zipfile
import tarfile
import gzip
import bz2
import lzma
import threading
from pathlib import Path

# Configuration
MAX_COMPRESSION_RATIO = 100  # 100:1 ratio = suspicious
MAX_EXTRACT_SIZE_MB = 1000   # Max 1GB total extracted
SCAN_EXTENSIONS = ['.zip', '.tar', '.gz', '.bz2', '.xz', '.7z']


class ZipBombDetector:
    def __init__(self):
        self.lock = threading.Lock()
        self.suspicious_files = []
        
    def calculate_extracted_size(self, file_path):
        """Estimate total extracted size without fully decompressing"""
        total_size = 0
        file_ext = Path(file_path).suffix.lower()
        
        try:
            if file_ext == '.zip':
                with zipfile.ZipFile(file_path, 'r') as zf:
                    for info in zf.infolist():
                        total_size += info.file_size
                        
            elif file_ext in ['.tar', '.gz', '.bz2', '.xz']:
                mode = 'r'
                if file_ext == '.tar':
                    mode = 'r'
                elif file_ext == '.gz':
                    mode = 'r:gz'
                elif file_ext == '.bz2':
                    mode = 'r:bz2'
                elif file_ext == '.xz':
                    mode = 'r:xz'
                    
                with tarfile.open(file_path, mode) as tf:
                    for member in tf.getmembers():
                        if member.isfile():
                            total_size += member.size
                            
        except Exception as e:
            print(f"Error scanning {file_path}: {e}")
            return None
            
        return total_size
        
    def scan_file(self, file_path):
        """Scan a file for zip bomb characteristics"""
        if not os.path.exists(file_path):
            return False
            
        file_ext = Path(file_path).suffix.lower()
        if file_ext not in SCAN_EXTENSIONS:
            return False
            
        compressed_size = os.path.getsize(file_path)
        extracted_size = self.calculate_extracted_size(file_path)
        
        if extracted_size is None:
            return False
            
        compression_ratio = extracted_size / compressed_size if compressed_size > 0 else 0
        extracted_size_mb = extracted_size / (1024 * 1024)
        
        print(f"[Zip Bomb Detector] Scanned: {file_path}")
        print(f"  Compressed size: {compressed_size / 1024:.2f} KB")
        print(f"  Extracted size:  {extracted_size_mb:.2f} MB")
        print(f"  Compression ratio: {compression_ratio:.2f}:1")
        
        is_suspicious = False
        
        if compression_ratio > MAX_COMPRESSION_RATIO:
            print(f"⚠️  SUSPICIOUS: High compression ratio!")
            is_suspicious = True
            
        if extracted_size_mb > MAX_EXTRACT_SIZE_MB:
            print(f"⚠️  SUSPICIOUS: Extracted size exceeds limit!")
            is_suspicious = True
            
        if is_suspicious:
            with self.lock:
                self.suspicious_files.append({
                    'path': file_path,
                    'compressed_size': compressed_size,
                    'extracted_size': extracted_size,
                    'ratio': compression_ratio
                })
            return True
            
        return False
        
    def get_suspicious_files(self):
        with self.lock:
            return list(self.suspicious_files)


# Example usage
if __name__ == "__main__":
    print("=" * 60)
    print("DEADBOLT ZIP BOMB DETECTOR")
    print("=" * 60)
    
    detector = ZipBombDetector()
    
    # Test with current directory
    test_dir = Path.cwd()
    print(f"\nScanning directory: {test_dir}\n")
    
    for file_path in test_dir.iterdir():
        if file_path.is_file():
            detector.scan_file(str(file_path))
            
    suspicious = detector.get_suspicious_files()
    if suspicious:
        print("\n" + "=" * 60)
        print(f"⚠️  FOUND {len(suspicious)} SUSPICIOUS FILES!")
        print("=" * 60)
        for i, f in enumerate(suspicious, 1):
            print(f"\n{i}. {f['path']}")
            print(f"   Ratio: {f['ratio']:.2f}:1")
            print(f"   Extracted: {f['extracted_size'] / (1024*1024):.2f} MB")
    else:
        print("\n✅ No suspicious files found!")
