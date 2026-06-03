import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from security_utils import SecurityUtils
from device_fingerprint import get_device_fingerprint

def test_security_utils():
    print("=== Testing Security Utils ===")
    
    # Test password validation
    good_pass = "DeadlockAdmin2024!"
    bad_pass_short = "Abc123!"
    bad_pass_no_upper = "deadlock2024!"
    bad_pass_no_lower = "DEADLOCK2024!"
    bad_pass_no_digit = "DeadlockAdmin!"
    bad_pass_no_special = "DeadlockAdmin2024"
    
    is_valid, _ = SecurityUtils.validate_password_complexity(good_pass)
    assert is_valid, "Good password should pass"
    
    is_valid, _ = SecurityUtils.validate_password_complexity(bad_pass_short)
    assert not is_valid, "Short password should fail"
    
    is_valid, _ = SecurityUtils.validate_password_complexity(bad_pass_no_upper)
    assert not is_valid, "Password without uppercase should fail"
    
    is_valid, _ = SecurityUtils.validate_password_complexity(bad_pass_no_lower)
    assert not is_valid, "Password without lowercase should fail"
    
    is_valid, _ = SecurityUtils.validate_password_complexity(bad_pass_no_digit)
    assert not is_valid, "Password without digit should fail"
    
    is_valid, _ = SecurityUtils.validate_password_complexity(bad_pass_no_special)
    assert not is_valid, "Password without special char should fail"
    
    print("✅ Security Utils tests passed!")

def test_device_fingerprint():
    print("\n=== Testing Device Fingerprinting ===")
    
    fingerprint = get_device_fingerprint()
    
    assert 'hostname' in fingerprint, "Hostname should be in fingerprint"
    assert 'os' in fingerprint, "OS should be in fingerprint"
    assert 'mac_address' in fingerprint, "MAC address should be in fingerprint"
    assert 'ip_addresses' in fingerprint, "IP addresses should be in fingerprint"
    assert 'username' in fingerprint, "Username should be in fingerprint"
    assert 'processor' in fingerprint, "Processor should be in fingerprint"
    
    print(f"✅ Fingerprint collected:")
    print(f"  Hostname: {fingerprint['hostname']}")
    print(f"  OS: {fingerprint['os']} {fingerprint.get('os_version', '')}")
    print(f"  MAC: {fingerprint['mac_address']}")
    print("✅ Device Fingerprint tests passed!")

if __name__ == "__main__":
    test_security_utils()
    test_device_fingerprint()
    print("\n🎉 All tests passed!")
