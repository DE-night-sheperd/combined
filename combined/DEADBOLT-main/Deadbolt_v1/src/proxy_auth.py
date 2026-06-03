import os
import sys
import time
import json
import hashlib
import threading
import requests
from pathlib import Path
from typing import Tuple, Optional


class ProxyAuthenticator:
    def __init__(self, config_dir: Path):
        self.config_dir = config_dir
        self.config_file = config_dir / "proxy_auth_config.json"
        self._load_config()

    def _load_config(self):
        if self.config_file.exists():
            try:
                with open(self.config_file, "r") as f:
                    self.config = json.load(f)
            except Exception as e:
                self.config = self._default_config()
        else:
            self.config = self._default_config()
            self._save_config()

    def _default_config(self):
        return {
            "proxy_server": "https://deadlock-auth.example.com",
            "device_id": hashlib.sha256(str(Path.home()).encode()).hexdigest(),
            "auth_interval": 300,  # seconds
            "last_auth_time": 0,
            "auth_token": None,
            "enabled": False
        }

    def _save_config(self):
        with open(self.config_file, "w") as f:
            json.dump(self.config, f, indent=2)

    def set_proxy_server(self, server_url: str):
        self.config["proxy_server"] = server_url
        self._save_config()

    def authenticate_with_proxy(self) -> Tuple[bool, str]:
        try:
            url = f"{self.config['proxy_server']}/api/authenticate"
            payload = {
                "device_id": self.config["device_id"],
                "timestamp": int(time.time())
            }
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.config["auth_token"] = data.get("token")
                self.config["last_auth_time"] = int(time.time())
                self._save_config()
                return True, "Authenticated with proxy successfully!"
            else:
                return False, f"Proxy authentication failed: {response.status_code}"
        except requests.exceptions.RequestException as e:
            return False, f"Failed to connect to proxy: {str(e)}"

    def verify_proxy_auth(self) -> Tuple[bool, str]:
        if not self.config["enabled"]:
            return True, "Proxy auth not enabled"
        
        time_since_last_auth = int(time.time()) - self.config.get("last_auth_time", 0)
        if time_since_last_auth < self.config.get("auth_interval", 300):
            return True, "Recent proxy auth still valid"
        
        return self.authenticate_with_proxy()

    def enable_proxy_auth(self):
        self.config["enabled"] = True
        self._save_config()

    def disable_proxy_auth(self):
        self.config["enabled"] = False
        self._save_config()

    def get_status(self):
        return {
            "enabled": self.config["enabled"],
            "proxy_server": self.config["proxy_server"],
            "device_id": self.config["device_id"],
            "last_auth_time": self.config["last_auth_time"],
            "has_token": self.config["auth_token"] is not None
        }


class ProxyAuthMonitor:
    def __init__(self, config_dir: Path):
        self.auth = ProxyAuthenticator(config_dir)
        self.running = False
        self.monitor_thread = None

    def start(self):
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()

    def stop(self):
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)

    def _monitor_loop(self):
        while self.running:
            time.sleep(60)
            if self.auth.config["enabled"]:
                verified, msg = self.auth.verify_proxy_auth()
                if not verified:
                    print(f"[Proxy Auth Monitor] {msg}")


if __name__ == "__main__":
    print("=== DEADLOCK PROXY AUTH TEST ===")
    test_config = Path.home() / ".deadlock_test"
    test_config.mkdir(parents=True, exist_ok=True)
    auth = ProxyAuthenticator(test_config)
    print("Current status:", auth.get_status())
    print("Testing verification (proxy disabled):", auth.verify_proxy_auth())
    print("\nEnabling proxy auth...")
    auth.enable_proxy_auth()
    print("Status after enabling:", auth.get_status())
