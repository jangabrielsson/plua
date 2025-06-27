#!/usr/bin/env python3
"""
Version bumping script for PLua
Usage: python scripts/bump_version.py [major|minor|patch]
"""

import sys
import re
import toml
from pathlib import Path


def bump_version(version_type='patch'):
    """Bump version in pyproject.toml and plua/version.py"""
    
    # Read current version from pyproject.toml
    pyproject_path = Path('pyproject.toml')
    if not pyproject_path.exists():
        print("Error: pyproject.toml not found")
        return False
    
    with open(pyproject_path, 'r') as f:
        data = toml.load(f)
    
    current_version = data['project']['version']
    print(f"Current version: {current_version}")
    
    # Parse version components
    match = re.match(r'(\d+)\.(\d+)\.(\d+)', current_version)
    if not match:
        print("Error: Could not parse version format")
        return False
    
    major, minor, patch = map(int, match.groups())
    
    # Bump version based on type
    if version_type == 'major':
        major += 1
        minor = 0
        patch = 0
    elif version_type == 'minor':
        minor += 1
        patch = 0
    elif version_type == 'patch':
        patch += 1
    else:
        print(f"Error: Invalid version type '{version_type}'. Use major, minor, or patch")
        return False
    
    new_version = f"{major}.{minor}.{patch}"
    print(f"New version: {new_version}")
    
    # Update pyproject.toml
    data['project']['version'] = new_version
    with open(pyproject_path, 'w') as f:
        toml.dump(data, f)
    print(f"Updated {pyproject_path}")
    
    # Update plua/version.py if it exists
    version_py_path = Path('plua/version.py')
    if version_py_path.exists():
        with open(version_py_path, 'r') as f:
            content = f.read()
        
        content = re.sub(
            r'__version__\s*=\s*["\']([^"\']+)["\']', 
            f'__version__ = "{new_version}"', 
            content
        )
        
        with open(version_py_path, 'w') as f:
            f.write(content)
        print(f"Updated {version_py_path}")
    
    return True


def main():
    if len(sys.argv) != 2:
        print("Usage: python scripts/bump_version.py [major|minor|patch]")
        sys.exit(1)
    
    version_type = sys.argv[1].lower()
    if version_type not in ['major', 'minor', 'patch']:
        print("Error: Version type must be major, minor, or patch")
        sys.exit(1)
    
    if bump_version(version_type):
        print("Version bumped successfully!")
    else:
        print("Failed to bump version")
        sys.exit(1)


if __name__ == "__main__":
    main() 