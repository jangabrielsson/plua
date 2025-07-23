#!/usr/bin/env python3
"""
Build script for creating a single-file plua2 executable using Nuitka

Prerequisites:
    pip install nuitka

Usage:
    python build_nuitka.py

This creates a fully compiled executable with excellent startup performance.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def build_nuitka():
    """Build plua2 using Nuitka for optimal performance"""
    
    project_root = Path(__file__).parent
    src_path = project_root / "src"
    static_path = project_root / "static"
    lua_path = src_path / "lua"
    
    # Ensure Nuitka is installed
    try:
        import nuitka
        # Get version through subprocess since nuitka module doesn't have __version__
        result = subprocess.run([sys.executable, "-m", "nuitka", "--version"], 
                              capture_output=True, text=True, check=True)
        version = result.stdout.strip().split('\n')[0]
        print(f"✓ Using Nuitka version: {version}")
    except ImportError:
        print("✗ Nuitka not found. Install with: pip install nuitka")
        sys.exit(1)
    except subprocess.CalledProcessError:
        print("✗ Nuitka installation appears corrupted")
        sys.exit(1)
    
    # Build command
    cmd = [
        sys.executable, "-m", "nuitka",
        
        # Main options
        "--onefile",                    # Single executable file
        "--assume-yes-for-downloads",   # Auto-download dependencies
        
        # Performance optimizations
        "--lto=yes",                   # Link-time optimization
        "--enable-plugin=upx",         # UPX compression (optional, needs upx installed)
        
        # Include data files
        f"--include-data-dir={static_path}=static",  # Web UI files
        f"--include-data-dir={lua_path}=lua",        # Lua runtime files
        
        # Include packages that might not be auto-detected
        "--include-package=lupa",
        "--include-package=aiohttp",
        "--include-package=fastapi",
        "--include-package=uvicorn",
        "--include-package=psutil",
        "--include-package=httpx",
        
        # Output options
        "--output-dir=dist",
        "--output-filename=plua2",
        
        # Entry point
        "build_main_standalone.py"
    ]
    
    print("🔨 Building plua2 with Nuitka...")
    print(f"Command: {' '.join(cmd)}")
    
    # Remove UPX plugin if UPX is not available
    if not shutil.which("upx"):
        print("⚠️  UPX not found, removing compression (install UPX for smaller binaries)")
        cmd = [arg for arg in cmd if not arg.startswith("--enable-plugin=upx")]
    
    try:
        result = subprocess.run(cmd, check=True, cwd=project_root)
        
        # Find the created executable
        dist_dir = project_root / "dist"
        executable_name = "plua2.exe" if sys.platform == "win32" else "plua2"
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
    build_nuitka()
