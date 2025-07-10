#!/usr/bin/env python3
"""
Build script for PLua executable using PyInstaller
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed:")
        print(f"  Return code: {e.returncode}")
        print(f"  stdout: {e.stdout}")
        print(f"  stderr: {e.stderr}")
        return False


def build_executable():
    """Build the PLua executable"""
    system = platform.system().lower()
    print(f"Building PLua executable for {system}")

    # Clean previous builds
    print("Cleaning previous builds...")
    for path in ['build', 'dist']:
        if os.path.exists(path):
            import shutil
            shutil.rmtree(path)

    # Build the executable with more robust options
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--clean',
        '--onefile',
        '--name=plua',
        '--add-data=src/lua:lua',
        '--add-data=src/extensions:extensions',
        '--add-data=pyproject.toml:.',
        '--hidden-import=lupa',
        '--hidden-import=lupa._lupa',
        '--hidden-import=lupa.lua',
        '--hidden-import=lupa.lua_types',
        '--hidden-import=asyncio',
        '--hidden-import=threading',
        '--hidden-import=socket',
        '--hidden-import=urllib.request',
        '--hidden-import=urllib.parse',
        '--hidden-import=urllib.error',
        '--hidden-import=ssl',
        '--hidden-import=json',
        '--hidden-import=time',
        '--hidden-import=os',
        '--hidden-import=sys',
        '--hidden-import=argparse',
        '--hidden-import=queue',
        '--hidden-import=requests',
        '--collect-all=lupa',
        '--collect-all=requests',
        '--collect-submodules=lupa',
        '--collect-submodules=plua',
        '--collect-submodules=extensions',
        'src/plua/__main__.py'
    ]

    if not run_command(cmd, "Building executable"):
        return False

    # Check if executable was created
    exe_name = 'plua.exe' if system == 'windows' else 'plua'
    exe_path = Path('dist') / exe_name

    if not exe_path.exists():
        print(f"✗ Executable not found at {exe_path}")
        return False

    print(f"✓ Executable created: {exe_path}")
    print(f"  Size: {exe_path.stat().st_size / (1024*1024):.1f} MB")

    # Test the executable
    print("Testing executable...")
    test_cmd = [str(exe_path), '--version']
    if run_command(test_cmd, "Testing executable"):
        print("✓ Executable test passed")
    else:
        print("✗ Executable test failed")
        return False

    return True


def main():
    """Main build function"""
    print("PLua Build Script")
    print("=" * 50)

    if not build_executable():
        print("\nBuild failed!")
        sys.exit(1)

    print("\nBuild completed successfully!")
    print("\nUsage:")
    print("  ./dist/plua script.lua")
    print("  ./dist/plua --debugger script.lua")
    print("  ./dist/plua --debugger --debugger-port 8188 script.lua")


if __name__ == '__main__':
    main()
