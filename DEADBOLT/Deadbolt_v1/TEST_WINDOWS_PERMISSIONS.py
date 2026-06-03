import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from file_access_control import FileAccessController, FileAccessRule

print("=" * 60)
print("DEADBOLT FILE ACCESS CONTROL - WINDOWS PERMISSIONS TEST")
print("=" * 60)

# Create test directory
test_dir = Path.home() / "DeadboltTestPermissions"
test_dir.mkdir(exist_ok=True)
test_file = test_dir / "protected_file.txt"

with open(test_file, 'w') as f:
    f.write("This is a protected test file!")

print(f"\nTest directory created: {test_dir}")
print(f"Test file created: {test_file}")

# Initialize controller
controller = FileAccessController()

print("\n--- Adding Windows permission rule ---")
rule = FileAccessRule(
    path=str(test_dir),
    rule_type="block_access",
    enabled=True,
    description="Test rule - block all access with Windows permissions"
)
controller.add_rule(rule)
print(f"Rule added and Windows permissions applied!")

print("\n--- Current Rules ---")
for i, r in enumerate(controller.get_rules()):
    print(f"  Rule {i+1}: {r.path} ({r.rule_type}) - {'Enabled' if r.enabled else 'Disabled'}")

print("\n" + "=" * 60)
print("Test complete! Check the test folder permissions in File Explorer!")
print("=" * 60)
