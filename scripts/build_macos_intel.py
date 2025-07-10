#!/usr/bin/env python3
"""
Build script for PLua macOS Intel executable using PyInstaller
"""

import os
import sys
import subprocess
import shutil
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


def build_macos_intel_executable():
    """Build the PLua executable for macOS Intel"""
    print("Building PLua executable for macOS Intel")

    # Check if we're on macOS
    if sys.platform != "darwin":
        print("This script is designed to run on macOS")
        return False

    # Clean previous builds
    print("Cleaning previous builds...")
    for path in ['build', 'dist']:
        if os.path.exists(path):
            shutil.rmtree(path)

    # Build the executable with Intel-specific options
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--clean',
        '--onefile',
        '--name=plua',
        '--add-data=src/lua:lua',
        '--add-data=src/extensions:extensions',
        '--add-data=examples:examples',
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
        '--target-arch=x86_64',  # Force Intel architecture
        'src/plua/__main__.py'
    ]

    if not run_command(cmd, "Building macOS Intel executable"):
        return False

    # Check if executable was created
    exe_path = Path('dist') / 'plua'

    if not exe_path.exists():
        print(f"✗ Executable not found at {exe_path}")
        return False

    print(f"✓ Executable created: {exe_path}")
    print(f"  Size: {exe_path.stat().st_size / (1024*1024):.1f} MB")

    # Verify architecture
    print("Verifying architecture...")
    arch_cmd = ['file', str(exe_path)]
    try:
        result = subprocess.run(arch_cmd, capture_output=True, text=True, check=True)
        print(f"  Architecture: {result.stdout.strip()}")
        if 'x86_64' in result.stdout:
            print("✓ Confirmed Intel x86_64 architecture")
        else:
            print("⚠ Warning: Executable may not be Intel x86_64")
    except subprocess.CalledProcessError:
        print("⚠ Could not verify architecture")

    # Test the executable
    print("Testing executable...")
    test_cmd = [str(exe_path), '--version']
    if run_command(test_cmd, "Testing executable"):
        print("✓ Executable test passed")
    else:
        print("✗ Executable test failed")
        return False

    return True


def create_macos_intel_package():
    """Create a macOS Intel package with all necessary files"""
    
    dist_dir = Path("dist")
    package_dir = Path("dist") / "plua_macos_intel"
    
    if not dist_dir.exists():
        print("Build directory not found. Run build_macos_intel_executable() first.")
        return False
    
    # Create package directory
    if package_dir.exists():
        shutil.rmtree(package_dir)
    package_dir.mkdir()
    
    # Copy executable
    exe_src = dist_dir / "plua"
    exe_dst = package_dir / "plua"
    if exe_src.exists():
        shutil.copy2(exe_src, exe_dst)
        # Make executable
        os.chmod(exe_dst, 0o755)
        print(f"Copied: {exe_src} -> {exe_dst}")
    
    # Copy additional files
    additional_files = [
        'README.md',
        'requirements.txt',
        'examples',
    ]
    
    for item in additional_files:
        src = Path(item)
        dst = package_dir / item
        if src.exists():
            if src.is_dir():
                shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)
            print(f"Copied: {src} -> {dst}")
    
    # Create a simple shell script for easy execution
    shell_content = '''#!/bin/bash
echo "PLua - Lua interpreter in Python"
echo "================================="
./plua "$@"
'''
    
    shell_file = package_dir / "plua.sh"
    with open(shell_file, 'w') as f:
        f.write(shell_content)
    
    # Make shell script executable
    os.chmod(shell_file, 0o755)
    
    print(f"\nmacOS Intel package created: {package_dir}")
    return True


def main():
    """Main build function"""
    print("PLua macOS Intel Build Script")
    print("=" * 50)

    if len(sys.argv) > 1 and sys.argv[1] == "package":
        # Create package
        if build_macos_intel_executable():
            create_macos_intel_package()
    else:
        # Just build executable
        build_macos_intel_executable()

    print("\nBuild completed successfully!")
    print("\nUsage:")
    print("  ./dist/plua script.lua")
    print("  ./dist/plua --debugger script.lua")
    print("  ./dist/plua --debugger --debugger-port 8188 script.lua")


if __name__ == '__main__':
    main() 