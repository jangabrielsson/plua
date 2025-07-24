#!/usr/bin/env python3
"""
Build script for creating a single-file plua executable using PyInstaller

Prerequisites:
    pip install pyinstaller

Usage:
    python build_pyinstaller.py

This creates a bundled executable with decent startup performance.
"""

import os
import sys
import subprocess
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def create_spec_file():
    """Create optimized PyInstaller spec file"""
    
    project_root = Path(__file__).parent
    src_path = project_root / "src"
    static_path = project_root / "static" 
    lua_path = src_path / "lua"
    
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

# Project paths
project_root = Path(r"{project_root}")
src_path = project_root / "src"
static_path = project_root / "static"
lua_path = src_path / "lua"

a = Analysis(
    [str(src_path / "plua" / "__main__.py")],
    pathex=[str(src_path)],
    binaries=[],
    datas=[
        (str(static_path), "static"),              # Web UI files
        (str(lua_path), "lua"),                    # Lua runtime files
    ],
    hiddenimports=[
        'lupa',
        'aiohttp.web',
        'aiohttp.web_runner', 
        'fastapi',
        'uvicorn.main',
        'uvicorn.config',
        'uvicorn.server',
        'psutil',
        'httpx',
        'json',
        'asyncio',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[
        'tkinter',      # GUI toolkit not needed
        'matplotlib',   # Plotting library not needed
        'numpy',        # May be pulled in by dependencies but not needed
        'PIL',          # Image processing not needed
        'pytest',       # Testing framework not needed
    ],
    noarchive=False,
    optimize=2,  # Maximum Python optimization
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='plua',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,       # Strip debug symbols
    upx=True,         # Use UPX compression if available
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    onefile=True,     # Single file executable
)
'''
    
    spec_path = project_root / "plua.spec"
    spec_path.write_text(spec_content)
    return spec_path

def build_pyinstaller():
    """Build plua using PyInstaller"""
    
    project_root = Path(__file__).parent
    
    # Ensure PyInstaller is installed
    try:
        import PyInstaller
        print(f"✓ Using PyInstaller version: {PyInstaller.__version__}")
    except ImportError:
        print("✗ PyInstaller not found. Install with: pip install pyinstaller")
        sys.exit(1)
    
    # Create optimized spec file
    spec_path = create_spec_file()
    print(f"✓ Created spec file: {spec_path}")
    
    # Build command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--clean",              # Clean cache and remove temp files
        "--noconfirm",         # Replace output directory without confirmation
        str(spec_path)
    ]
    
    print("🔨 Building plua with PyInstaller...")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, cwd=project_root)
        
        # Find the created executable
        dist_dir = project_root / "dist"
        executable_name = "plua.exe" if sys.platform == "win32" else "plua"
        executable_path = dist_dir / executable_name
        
        if executable_path.exists():
            size_mb = executable_path.stat().st_size / (1024 * 1024)
            print(f"✓ Build successful!")
            print(f"  Executable: {executable_path}")
            print(f"  Size: {size_mb:.1f} MB")
            print(f"  Test with: {executable_path} --help")
        else:
            print("✗ Executable not found in expected location")
            
    except subprocess.CalledProcessError as e:
        print(f"✗ Build failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build_pyinstaller()
