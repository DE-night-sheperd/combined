import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from file_access_control import FileAccessController, FileAccessRule

print("=" * 60)
print("DEADBOLT FILE ACCESS CONTROL - TEST SCRIPT")
print("=" * 60)

# Create test directory
test_dir = Path.home() / "DeadboltTestFolder"
test_dir.mkdir(exist_ok=True)
test_file = test_dir / "test_file.txt"

with open(test_file, 'w') as f:
    f.write("This is a test file!")

print(f"\nTest directory created: {test_dir}")
print(f"Test file created: {test_file}")

# Initialize controller
controller = FileAccessController()

print("\n--- Adding access rule ---")
rule = FileAccessRule(
    path=str(test_dir),
    rule_type="block_access",
    enabled=True,
    description="Test rule - block all access to test folder"
)
controller.add_rule(rule)
print(f"Rule added: {rule.path}")

print("\n--- Testing file access (user-mode check) ---")
test_path = str(test_file)
operations = ['read', 'write', 'delete']
for op in operations:
    blocked = controller.should_block_operation(test_path, op)
    status = "BLOCKED" if blocked else "ALLOWED"
    print(f"  {op.upper()}: {status}")

print("\n--- Current Rules ---")
for i, r in enumerate(controller.get_rules()):
    print(f"  Rule {i+1}: {r.path} ({r.rule_type}) - {'Enabled' if r.enabled else 'Disabled'}")

print("\nTest completed!")
print("=" * 60)
