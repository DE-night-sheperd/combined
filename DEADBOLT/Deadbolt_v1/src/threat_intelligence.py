import os
import json
import hashlib
import time
from pathlib import Path
import threading


class ThreatIntelligenceFeed:
    def __init__(self, config_dir=None):
        self.config_dir = Path(config_dir) if config_dir else Path.home() / ".deadlock"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.threat_db_file = self.config_dir / "threat_intelligence.json"
        self.update_log_file = self.config_dir / "threat_updates.log"
        
        self.lock = threading.Lock()
        self._load_threat_db()
        
    def _load_threat_db(self):
        if self.threat_db_file.exists():
            try:
                with open(self.threat_db_file, "r") as f:
                    self.threat_db = json.load(f)
            except:
                self.threat_db = self._default_threat_db()
                self._save_threat_db()
        else:
            self.threat_db = self._default_threat_db()
            self._save_threat_db()
            
    def _default_threat_db(self):
        return {
            "version": "1.0",
            "last_updated": time.time(),
            "file_hashes": {
                "malicious": [],
                "suspicious": []
            },
            "ip_addresses": {
                "malicious": [],
                "suspicious": []
            },
            "domains": {
                "malicious": [],
                "suspicious": []
            },
            "urls": {
                "malicious": [],
                "suspicious": []
            },
            "signatures": {
                "ransomware_extensions": [
                    ".locky", ".zepto", ".wannacry", ".cryptolocker", ".petya",
                    ".notpetya", ".cerber", ".teslacrypt", ".xtbl", ".aaa", ".abc",
                    ".xyz", ".zzz", ".micro", ".delta", ".gws", ".onion", ".ft",
                    ".kraken", ".lock", ".encrypted", ".crypto", ".codercrypt",
                    ".ryuk", ".maze", ".doppelpaymer", ".conti", ".clop", ".avaddon"
                ],
                "suspicious_keywords": [
                    "encrypt", "decrypt", "ransom", "bitcoin", "pay", "decryptor",
                    "your_files_are_encrypted", "readme", "how_to_back", "instructions",
                    "tor", "darkweb", "payment", "wallet"
                ]
            }
        }
        
    def _save_threat_db(self):
        with open(self.threat_db_file, "w") as f:
            json.dump(self.threat_db, f, indent=2)
            
    def _log_update(self, message):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        with open(self.update_log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)
            
    def _get_file_hash(self, file_path):
        try:
            hasher = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except:
            return None
            
    def check_file_hash(self, file_path):
        file_hash = self._get_file_hash(file_path)
        if not file_hash:
            return {"is_malicious": False, "is_suspicious": False, "details": "Could not compute hash"}
            
        if file_hash in self.threat_db["file_hashes"]["malicious"]:
            return {"is_malicious": True, "is_suspicious": False, "details": f"Known malicious hash: {file_hash}"}
            
        if file_hash in self.threat_db["file_hashes"]["suspicious"]:
            return {"is_malicious": False, "is_suspicious": True, "details": f"Suspicious hash: {file_hash}"}
            
        return {"is_malicious": False, "is_suspicious": False, "details": "Hash not in threat database"}
        
    def check_ip(self, ip_address):
        if ip_address in self.threat_db["ip_addresses"]["malicious"]:
            return {"is_malicious": True, "is_suspicious": False, "details": f"Known malicious IP: {ip_address}"}
            
        if ip_address in self.threat_db["ip_addresses"]["suspicious"]:
            return {"is_malicious": False, "is_suspicious": True, "details": f"Suspicious IP: {ip_address}"}
            
        return {"is_malicious": False, "is_suspicious": False, "details": "IP not in threat database"}
        
    def check_domain(self, domain):
        domain = domain.lower()
        if domain in self.threat_db["domains"]["malicious"]:
            return {"is_malicious": True, "is_suspicious": False, "details": f"Known malicious domain: {domain}"}
            
        if domain in self.threat_db["domains"]["suspicious"]:
            return {"is_malicious": False, "is_suspicious": True, "details": f"Suspicious domain: {domain}"}
            
        return {"is_malicious": False, "is_suspicious": False, "details": "Domain not in threat database"}
        
    def check_url(self, url):
        url = url.lower()
        if url in self.threat_db["urls"]["malicious"]:
            return {"is_malicious": True, "is_suspicious": False, "details": f"Known malicious URL: {url}"}
            
        if url in self.threat_db["urls"]["suspicious"]:
            return {"is_malicious": False, "is_suspicious": True, "details": f"Suspicious URL: {url}"}
            
        return {"is_malicious": False, "is_suspicious": False, "details": "URL not in threat database"}
        
    def add_malicious_hash(self, file_hash):
        with self.lock:
            if file_hash not in self.threat_db["file_hashes"]["malicious"]:
                self.threat_db["file_hashes"]["malicious"].append(file_hash)
                self.threat_db["last_updated"] = time.time()
                self._save_threat_db()
                self._log_update(f"Added malicious hash: {file_hash}")
                return True
        return False
        
    def add_suspicious_hash(self, file_hash):
        with self.lock:
            if file_hash not in self.threat_db["file_hashes"]["suspicious"]:
                self.threat_db["file_hashes"]["suspicious"].append(file_hash)
                self.threat_db["last_updated"] = time.time()
                self._save_threat_db()
                self._log_update(f"Added suspicious hash: {file_hash}")
                return True
        return False
        
    def add_malicious_ip(self, ip):
        with self.lock:
            if ip not in self.threat_db["ip_addresses"]["malicious"]:
                self.threat_db["ip_addresses"]["malicious"].append(ip)
                self.threat_db["last_updated"] = time.time()
                self._save_threat_db()
                self._log_update(f"Added malicious IP: {ip}")
                return True
        return False
        
    def add_malicious_domain(self, domain):
        domain = domain.lower()
        with self.lock:
            if domain not in self.threat_db["domains"]["malicious"]:
                self.threat_db["domains"]["malicious"].append(domain)
                self.threat_db["last_updated"] = time.time()
                self._save_threat_db()
                self._log_update(f"Added malicious domain: {domain}")
                return True
        return False
        
    def get_threat_stats(self):
        return {
            "version": self.threat_db["version"],
            "last_updated": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.threat_db["last_updated"])),
            "malicious_hashes": len(self.threat_db["file_hashes"]["malicious"]),
            "suspicious_hashes": len(self.threat_db["file_hashes"]["suspicious"]),
            "malicious_ips": len(self.threat_db["ip_addresses"]["malicious"]),
            "suspicious_ips": len(self.threat_db["ip_addresses"]["suspicious"]),
            "malicious_domains": len(self.threat_db["domains"]["malicious"]),
            "suspicious_domains": len(self.threat_db["domains"]["suspicious"]),
            "ransomware_extensions": len(self.threat_db["signatures"]["ransomware_extensions"])
        }


if __name__ == "__main__":
    print("=== DEADLOCK THREAT INTELLIGENCE FEED ===")
    feed = ThreatIntelligenceFeed()
    
    print("\nThreat database stats:")
    stats = feed.get_threat_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
