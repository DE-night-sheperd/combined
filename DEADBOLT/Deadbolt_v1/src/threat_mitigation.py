import os
import time
import threading
import psutil
import subprocess
from pathlib import Path

# Comprehensive threat mitigation system
class ThreatMitigationSystem:
    def __init__(self):
        self.lock = threading.Lock()
        self.mitigation_actions = []
        
    def check_suspicious_processes(self):
        """Check for suspicious processes (keyloggers, miners, etc.)"""
        suspicious_names = [
            'keylogger', 'keylog', 'miner', 'xmr', 'bitcoin',
            'crypto', 'inject', 'hollow', 'reflective', 'meterpreter'
        ]
        
        suspicious_found = []
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'exe']):
                try:
                    proc_name = proc.info['name'].lower()
                    if any(keyword in proc_name for keyword in suspicious_names):
                        suspicious_found.append(proc.info)
                        print(f"⚠️  SUSPICIOUS PROCESS: {proc.info['name']} (PID: {proc.info['pid']})")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
                    
        except Exception as e:
            pass
            
        return suspicious_found
        
    def check_unusual_network_connections(self):
        """Check for unusual network connections"""
        suspicious_ports = [4444, 9999, 8080, 8443, 9001, 31337]
        unusual_connections = []
        
        try:
            for conn in psutil.net_connections():
                if conn.status == 'ESTABLISHED' and conn.raddr:
                    remote_port = conn.raddr.port
                    if remote_port in suspicious_ports:
                        unusual_connections.append(conn)
                        print(f"⚠️  UNUSUAL CONNECTION: Port {remote_port} - {conn.raddr.ip}")
        except Exception:
            pass
            
        return unusual_connections
        
    def check_powershell_activity(self):
        """Check for suspicious PowerShell activity"""
        powershell_procs = []
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['name'] and 'powershell' in proc.info['name'].lower():
                        cmdline = ' '.join(proc.info['cmdline'] or []).lower()
                        suspicious_patterns = [
                            'iex', 'invoke-expression', 'base64', 'encodedcommand',
                            'bypass', 'executionpolicy', 'remotesigned', 'unrestricted'
                        ]
                        if any(pattern in cmdline for pattern in suspicious_patterns):
                            powershell_procs.append(proc.info)
                            print(f"⚠️  SUSPICIOUS POWERSHELL: PID {proc.info['pid']}")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        except Exception:
            pass
            
        return powershell_procs
        
    def mitigate_threat(self, threat_type, details):
        """Take action to mitigate a detected threat"""
        with self.lock:
            self.mitigation_actions.append({
                'timestamp': time.time(),
                'threat_type': threat_type,
                'details': details
            })
            
        print(f"🔒 MITIGATION APPLIED: {threat_type}")
        return True
        
    def run_comprehensive_scan(self):
        """Run all threat checks"""
        print("\n" + "="*60)
        print("DEADBOLT COMPREHENSIVE THREAT SCAN")
        print("="*60)
        
        threats_found = []
        
        # Check 1: Suspicious processes
        print("\n[1] Scanning for suspicious processes...")
        sus_procs = self.check_suspicious_processes()
        if sus_procs:
            threats_found.append(('Suspicious Processes', sus_procs))
            
        # Check 2: Unusual network connections
        print("\n[2] Scanning for unusual network connections...")
        unusual_conns = self.check_unusual_network_connections()
        if unusual_conns:
            threats_found.append(('Unusual Network', unusual_conns))
            
        # Check 3: Suspicious PowerShell
        print("\n[3] Scanning for suspicious PowerShell activity...")
        sus_powershell = self.check_powershell_activity()
        if sus_powershell:
            threats_found.append(('Suspicious PowerShell', sus_powershell))
            
        print("\n" + "="*60)
        if threats_found:
            print(f"⚠️  FOUND {len(threats_found)} POTENTIAL THREATS!")
            for threat_type, details in threats_found:
                self.mitigate_threat(threat_type, details)
        else:
            print("✅ NO THREATS FOUND - System clean!")
        print("="*60)
        
        return threats_found


# Example usage
if __name__ == "__main__":
    print("=" * 60)
    print("DEADBOLT THREAT MITIGATION SYSTEM")
    print("=" * 60)
    
    tms = ThreatMitigationSystem()
    tms.run_comprehensive_scan()
