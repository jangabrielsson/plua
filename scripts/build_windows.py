#!/usr/bin/env python3
"""
Cross-compilation script for building PLua for Windows from macOS
"""

import sys
import subprocess
import shutil
from pathlib import Path


def run_command(cmd, cwd=None):
    """Run a command and return the result"""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False
    print(f"Success: {result.stdout}")
    return True


def build_windows_executable():
    """Build Windows executable using PyInstaller"""
    
    # Check if we're on macOS
    if sys.platform != "darwin":
        print("This script is designed to run on macOS for cross-compilation to Windows")
        return False
    
    # Create build directory
    build_dir = Path("build_windows")
    build_dir.mkdir(exist_ok=True)
    
    # Create a spec file for PyInstaller
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/plua/__main__.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src/lua', 'lua'),
        ('src/extensions', 'extensions'),
        ('examples', 'examples'),
    ],
    hiddenimports=[
        'lupa',
        'asyncio',
        'socket',
        'threading',
        'urllib.request',
        'urllib.parse',
        'urllib.error',
        'ssl',
        'paho.mqtt.client',
        'extensions.network_extensions',
        'extensions.html_extensions',
        'extensions.core',
        'extensions.registry',
        'plua',
        'plua.interpreter',
        'plua.embedded_api_server',
        'plua.version',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='plua',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
'''
    
    spec_file = build_dir / "plua.spec"
    with open(spec_file, 'w') as f:
        f.write(spec_content)
    
    # Install required packages for Windows
    print("Installing required packages...")
    packages = [
        'lupa',
        'paho-mqtt',
        'pyinstaller',
    ]
    
    for package in packages:
        if not run_command([sys.executable, '-m', 'pip', 'install', package]):
            return False
    
    # Build the executable
    print("Building Windows executable...")
    if not run_command([
        sys.executable, '-m', 'PyInstaller',
        '--distpath', str(build_dir / 'dist'),
        '--workpath', str(build_dir / 'build'),
        str(spec_file)
    ]):
        return False
    
    print("\nBuild completed successfully!")
    print(f"Windows executable: {build_dir / 'dist' / 'plua.exe'}")
    return True


def create_windows_package():
    """Create a Windows package with all necessary files"""
    
    build_dir = Path("build_windows")
    dist_dir = build_dir / "dist"
    package_dir = build_dir / "plua_windows"
    
    if not dist_dir.exists():
        print("Build directory not found. Run build_windows_executable() first.")
        return False
    
    # Create package directory
    if package_dir.exists():
        shutil.rmtree(package_dir)
    package_dir.mkdir()
    
    # Copy executable
    exe_src = dist_dir / "plua.exe"
    exe_dst = package_dir / "plua.exe"
    if exe_src.exists():
        shutil.copy2(exe_src, exe_dst)
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
    
    # Create a simple batch file for easy execution
    batch_content = '''@echo off
echo PLua - Lua interpreter in Python
echo ================================
plua.exe %*
'''
    
    batch_file = package_dir / "plua.bat"
    with open(batch_file, 'w') as f:
        f.write(batch_content)
    
    print(f"\nWindows package created: {package_dir}")
    return True


if __name__ == "__main__":
    print("PLua Windows Cross-Compilation")
    print("=" * 40)
    
    if len(sys.argv) > 1 and sys.argv[1] == "package":
        # Create package
        if build_windows_executable():
            create_windows_package()
    else:
        # Just build executable
        build_windows_executable() 