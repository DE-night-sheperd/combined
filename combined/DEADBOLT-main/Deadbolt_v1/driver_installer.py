import os
import sys
import ctypes
import subprocess
from pathlib import Path
import time


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def run_command_as_admin(cmd):
    try:
        if is_admin():
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode == 0, result.stdout, result.stderr
        else:
            return False, "Admin privileges required", "Please run as administrator"
    except Exception as e:
        return False, "", str(e)


class DeadlockDriverInstaller:
    def __init__(self, install_dir=None):
        self.install_dir = Path(install_dir) if install_dir else Path(__file__).parent
        self.drivers_dir = self.install_dir / "Deadbolt_Drivers"
        self.driver_names = [
            "DeadboltMinifilter",
            "DeadboltMonitor", 
            "DeadboltMonitor_Extended"
        ]

    def check_wdk_tools(self):
        """Check if we have necessary tools (for dev only)"""
        tools = ["sc.exe", "pnputil.exe"]
        for tool in tools:
            try:
                subprocess.run(
                    [tool, "/?"],
                    capture_output=True,
                    timeout=5
                )
            except FileNotFoundError:
                print(f"[Driver Installer] Warning: {tool} not found")
        return True

    def enable_test_signing(self):
        """Enable test signing mode (for development/testing)"""
        print("[Driver Installer] Enabling test signing mode...")
        success, stdout, stderr = run_command_as_admin(
            "bcdedit /set testsigning on"
        )
        if success:
            print("[Driver Installer] Test signing enabled - reboot required!")
        else:
            print(f"[Driver Installer] Failed to enable test signing: {stderr}")
        return success

    def install_driver_package(self, driver_name):
        """Install a driver package using pnputil"""
        inf_path = self.drivers_dir / driver_name / f"{driver_name}.inf"
        
        if not inf_path.exists():
            print(f"[Driver Installer] INF not found: {inf_path}")
            return False

        print(f"[Driver Installer] Installing driver package: {driver_name}")
        success, stdout, stderr = run_command_as_admin(
            f'pnputil /add-driver "{inf_path}" /install'
        )
        
        if success:
            print(f"[Driver Installer] Successfully staged driver: {driver_name}")
        else:
            print(f"[Driver Installer] Failed to install driver {driver_name}: {stderr}")
        return success

    def create_driver_service(self, driver_name, bin_path):
        """Create driver service using sc.exe"""
        print(f"[Driver Installer] Creating service for: {driver_name}")
        success, stdout, stderr = run_command_as_admin(
            f'sc create {driver_name} type= kernel binPath= "{bin_path}"'
        )
        if success:
            print(f"[Driver Installer] Service created: {driver_name}")
        else:
            print(f"[Driver Installer] Failed to create service {driver_name}: {stderr}")
        return success

    def start_driver_service(self, driver_name):
        """Start a driver service"""
        print(f"[Driver Installer] Starting service: {driver_name}")
        success, stdout, stderr = run_command_as_admin(
            f"sc start {driver_name}"
        )
        if success:
            print(f"[Driver Installer] Service started: {driver_name}")
        else:
            print(f"[Driver Installer] Failed to start service {driver_name}: {stderr}")
        return success

    def install_all_drivers(self):
        """Main installation function"""
        print("[Driver Installer] =======================================")
        print("[Driver Installer] Deadlock Driver Installer")
        print("[Driver Installer] =======================================")
        
        if not is_admin():
            print("[Driver Installer] ERROR: Please run as administrator!")
            return False

        if not self.drivers_dir.exists():
            print(f"[Driver Installer] ERROR: Drivers directory not found: {self.drivers_dir}")
            return False

        print(f"[Driver Installer] Installing drivers from: {self.drivers_dir}")
        
        success_count = 0
        for driver_name in self.driver_names:
            if self.install_driver_package(driver_name):
                success_count += 1

        print(f"[Driver Installer] =======================================")
        print(f"[Driver Installer] Installation complete!")
        print(f"[Driver Installer] Drivers staged: {success_count}/{len(self.driver_names)}")
        print(f"[Driver Installer] NOTE: For unsigned drivers, enable test signing and reboot!")
        print("[Driver Installer] =======================================")
        
        return success_count > 0


if __name__ == "__main__":
    installer = DeadlockDriverInstaller()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--testsigning":
            installer.enable_test_signing()
        elif sys.argv[1] == "--install":
            installer.install_all_drivers()
    else:
        installer.install_all_drivers()
