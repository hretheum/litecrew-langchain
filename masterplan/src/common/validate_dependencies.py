# validate_dependencies.py
import subprocess
import sys
import re

def check_command(cmd, expected_pattern=None, min_version=None):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            return False, f"Command failed: {result.stderr}"
        
        output = result.stdout.strip()
        
        if expected_pattern and not re.search(expected_pattern, output):
            return False, f"Pattern '{expected_pattern}' not found in output"
        
        if min_version:
            # Extract version and compare
            version_match = re.search(r'(\d+\.\d+)', output)
            if version_match:
                version = float(version_match.group(1))
                if version < min_version:
                    return False, f"Version {version} < required {min_version}"
        
        return True, output
    except Exception as e:
        return False, str(e)

checks = [
    ("Python 3.11", "python3.11 --version", r"3\.11\.", None),
    ("Redis", "redis-cli ping", "PONG", None),
    ("SQLite", "sqlite3 --version", r"\d+\.\d+", 3.40),
    ("Nginx", "nginx -v", "nginx", None),
    ("Supervisor", "supervisord --version", r"\d+\.\d+", None),
    ("Swap", "free -h | grep Swap", r"[0-9]+G", None),
]

all_passed = True
for name, cmd, pattern, min_ver in checks:
    passed, output = check_command(cmd, pattern, min_ver)
    status = "✅" if passed else "❌"
    print(f"{status} {name}: {output}")
    if not passed:
        all_passed = False

sys.exit(0 if all_passed else 1)