import os
import sys
import json
import time
import threading
import subprocess
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))
from threat_intelligence import ThreatIntelligenceFeed


class NetworkFirewall:
    def __init__(self, config_dir=None):
        self.config_dir = Path(config_dir) if config_dir else Path.home() / ".deadlock"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.firewall_config_file = self.config_dir / "network_firewall_config.json"
        self.network_log_file = self.config_dir / "network_traffic.log"
        
        self.threat_feed = ThreatIntelligenceFeed(self.config_dir)
        
        self.running = False
        self.monitor_thread = None
        self.lock = threading.Lock()
        
        self._load_config()
        
    def _load_config(self):
        if self.firewall_config_file.exists():
            try:
                with open(self.firewall_config_file, "r") as f:
                    self.config = json.load(f)
            except:
                self.config = self._default_config()
                self._save_config()
        else:
            self.config = self._default_config()
            self._save_config()
            
    def _default_config(self):
        return {
            "enabled": True,
            "block_malicious_ips": True,
            "block_c2_servers": True,
            "allowed_ports": [80, 443, 53],
            "blocked_ips": [],
            "blocked_domains": []
        }
        
    def _save_config(self):
        with open(self.firewall_config_file, "w") as f:
            json.dump(self.config, f, indent=2)
            
    def _log_event(self, message):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        with open(self.network_log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)
        print(f"[Network Firewall] {message}")
        
    def get_active_connections(self):
        connections = []
        try:
            import wmi
            wmi_c = wmi.WMI()
            net_conns = wmi_c.Win32_NetworkConnection()
            for nc in net_conns:
                try:
                    conn_info = {
                        "remote_ip": getattr(nc, "RemoteName", ""),
                        "local_port": getattr(nc, "LocalName", ""),
                        "status": getattr(nc, "Status", "")
                    }
                    connections.append(conn_info)
                except:
                    pass
        except Exception as e:
            pass
        return connections
        
    def check_connection(self, remote_ip, remote_domain=None):
        if not self.config["enabled"]:
            return {"allowed": True, "reason": "Firewall disabled"}
            
        if remote_ip:
            result = self.threat_feed.check_ip(remote_ip)
            if result["is_malicious"]:
                return {"allowed": False, "reason": result["details"]}
                
        if remote_domain:
            result = self.threat_feed.check_domain(remote_domain)
            if result["is_malicious"]:
                return {"allowed": False, "reason": result["details"]}
                
        if remote_ip in self.config["blocked_ips"]:
            return {"allowed": False, "reason": "IP in blocked list"}
            
        if remote_domain and remote_domain in self.config["blocked_domains"]:
            return {"allowed": False, "reason": "Domain in blocked list"}
            
        return {"allowed": True, "reason": "Connection allowed"}
        
    def block_ip(self, ip_address):
        with self.lock:
            if ip_address not in self.config["blocked_ips"]:
                self.config["blocked_ips"].append(ip_address)
                self._save_config()
                self._log_event(f"Blocked IP: {ip_address}")
                return True
        return False
        
    def block_domain(self, domain):
        domain = domain.lower()
        with self.lock:
            if domain not in self.config["blocked_domains"]:
                self.config["blocked_domains"].append(domain)
                self._save_config()
                self._log_event(f"Blocked domain: {domain}")
                return True
        return False
        
    def get_firewall_status(self):
        return {
            "enabled": self.config["enabled"],
            "block_malicious_ips": self.config["block_malicious_ips"],
            "block_c2_servers": self.config["block_c2_servers"],
            "blocked_ips_count": len(self.config["blocked_ips"]),
            "blocked_domains_count": len(self.config["blocked_domains"])
        }
        
    def monitor_loop(self):
        while self.running:
            time.sleep(5)
            
    def start(self):
        if self.running:
            return
        self.running = True
        self._log_event("Network Firewall started")
        self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
        self.monitor_thread.start()
        
    def stop(self):
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=3)
        self._log_event("Network Firewall stopped")


if __name__ == "__main__":
    print("=== DEADLOCK NETWORK FIREWALL ===")
    fw = NetworkFirewall()
    
    print("\nCurrent status:")
    status = fw.get_firewall_status()
    for key, value in status.items():
        print(f"  {key}: {value}")
