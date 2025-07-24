#!/usr/bin/env python3
"""
Build script for creating a single-file plua executable using Nuitka

Prerequisites:
    pip install nuitka

Usage:
    python build_nuitka.py

This creates a fully compiled executable with excellent startup performance.
"""

import sys
import subprocess
import shutil
from pathlib import Path
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


def build_nuitka():
    """Build plua using Nuitka for optimal performance"""
    
    project_root = Path(__file__).parent
    src_path = project_root / "src"
    static_path = project_root.parent / "static"
    lua_path = src_path / "lua"
    
    # Ensure Nuitka is installed
    try:
        # Get version through subprocess since nuitka module doesn't have __version__
        cmd = [sys.executable, "-m", "nuitka", "--version"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        version = result.stdout.strip().split('\n')[0]
        print(f"[OK] Using Nuitka version: {version}")
    except ImportError:
        print("[ERROR] Nuitka not found. Install with: pip install nuitka")
        sys.exit(1)
    except subprocess.CalledProcessError:
        print("[ERROR] Nuitka installation appears corrupted")
        sys.exit(1)
    
    # Dynamically include all Lua files
    data_file_args = []
    for file in lua_path.glob("**/*"):
        if file.is_file():
            rel_path = file.relative_to(lua_path)
            data_file_args.append(f"--include-data-file={file}=lua/{rel_path}")
    
    # Build command
    cmd = [
        sys.executable, "-m", "nuitka",
        "--onefile",                    # Single executable file
        "--assume-yes-for-downloads",   # Auto-download dependencies
        "--lto=yes",                   # Link-time optimization
        "--enable-plugin=upx",         # UPX compression (optional, needs upx installed)
        f"--include-data-dir={static_path}=static",  # Web UI files
        # Lua files included individually below
        *data_file_args,
        # Include packages that might not be auto-detected
        "--include-package=lupa",
        "--include-package=aiohttp",
        "--include-package=fastapi",
        "--include-package=uvicorn",
        "--include-package=psutil",
        "--include-package=httpx",
        "--output-dir=dist",
        "--output-filename=plua",
        "build_main_standalone.py"
    ]
    
    print("[BUILD] Building plua with Nuitka...")
    print(f"Command: {' '.join(cmd)}")
    
    # Remove UPX plugin if UPX is not available
    if not shutil.which("upx"):
        print("[WARN] UPX not found, removing compression (install UPX for smaller binaries)")
        cmd = [arg for arg in cmd if not arg.startswith("--enable-plugin=upx")]
    
    try:
        result = subprocess.run(cmd, check=True, cwd=project_root)
        
        # Find the created executable
        dist_dir = project_root / "dist"
        executable_name = "plua.exe" if sys.platform == "win32" else "plua"
        executable_path = dist_dir / executable_name
        
        if executable_path.exists():
            size_mb = executable_path.stat().st_size / (1024 * 1024)
            print("[OK] Build successful!")
            print(f"  Executable: {executable_path}")
            print(f"  Size: {size_mb:.1f} MB")
            print(f"  Test with: {executable_path} --help")
        else:
            print("[ERROR] Executable not found in expected location")
            
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Build failed with exit code {e.returncode}")
        sys.exit(1)


if __name__ == "__main__":
    build_nuitka()
