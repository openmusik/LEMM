"""
Test requirements.txt for HuggingFace Space deployment
Validates that all packages are installable and no duplicates exist
"""
import re
from pathlib import Path

def parse_requirements(file_path):
    """Parse requirements.txt and extract package names"""
    packages = []
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue
            
            # Extract package name (before ==, >=, etc.)
            if line.startswith('git+'):
                # Git packages
                packages.append('ACE-Step (git)')
            else:
                # Regular packages
                match = re.match(r'^([a-zA-Z0-9_-]+)', line)
                if match:
                    packages.append(match.group(1).lower())
    
    return packages

def check_duplicates(packages):
    """Check for duplicate packages"""
    seen = set()
    duplicates = []
    
    for pkg in packages:
        if pkg in seen:
            duplicates.append(pkg)
        seen.add(pkg)
    
    return duplicates

def check_problematic_packages(file_path):
    """Check for known problematic packages"""
    problematic = {
        'essentia': 'No stable release, only dev versions',
        'aubio': 'Not used in LEMM',
        'fastapi': 'Optional API not implemented',
        'uvicorn': 'Not needed for Gradio'
    }
    
    found_problems = []
    with open(file_path, 'r') as f:
        content = f.read().lower()
        for pkg, reason in problematic.items():
            if pkg in content:
                found_problems.append(f"{pkg}: {reason}")
    
    return found_problems

# Test requirements.txt
print("🧪 Testing HuggingFace Space Requirements\n")

req_file = Path(__file__).parent / "huggingface_space_deploy" / "requirements.txt"

if not req_file.exists():
    print(f"❌ File not found: {req_file}")
    exit(1)

print(f"📄 Checking: {req_file.name}\n")

# Parse packages
packages = parse_requirements(req_file)
print(f"📦 Total packages: {len(packages)}")
print(f"   Packages: {', '.join(packages[:10])}")
if len(packages) > 10:
    print(f"   ... and {len(packages) - 10} more\n")
else:
    print()

# Check for duplicates
duplicates = check_duplicates(packages)
if duplicates:
    print(f"❌ DUPLICATES FOUND: {', '.join(duplicates)}")
    exit(1)
else:
    print("✅ No duplicate packages\n")

# Check for problematic packages
problems = check_problematic_packages(req_file)
if problems:
    print("❌ PROBLEMATIC PACKAGES FOUND:")
    for problem in problems:
        print(f"   - {problem}")
    exit(1)
else:
    print("✅ No problematic packages\n")

# Check for essential packages
essential = [
    'torch', 'gradio', 'demucs', 'librosa', 'pedalboard',
    'huggingface_hub', 'datasets', 'numpy', 'pyyaml'
]

missing = []
for pkg in essential:
    if pkg not in packages:
        missing.append(pkg)

if missing:
    print(f"⚠️  Missing essential packages: {', '.join(missing)}\n")
else:
    print("✅ All essential packages present\n")

# Summary
print("="*50)
if not duplicates and not problems and not missing:
    print("🎉 Requirements file is VALID and ready for deployment!")
    print("="*50)
    exit(0)
else:
    print("❌ Requirements file has ISSUES that need fixing")
    print("="*50)
    exit(1)
