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
    scripts_dir = project_root
    # Go up one level to get to the actual project root
    actual_project_root = project_root.parent
    src_path = actual_project_root / "src"
    static_path = src_path / "plua" / "static"  # Correct path to static files
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
    
    # Build command base
    cmd = [
        sys.executable, "-m", "nuitka",
        "--assume-yes-for-downloads",   # Auto-download dependencies
        "--lto=yes",                   # Link-time optimization
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
    
    # Add platform-specific mode flags and UPX handling
    if sys.platform == "darwin":
        cmd.insert(3, "--mode=app")  # Required for Foundation framework on macOS
        cmd.insert(4, "--macos-app-icon=none")  # Disable dock icon warning
        print("[INFO] macOS detected: Using --mode=app for Foundation framework compatibility")
        # Skip UPX on macOS as it often fails with native frameworks
        print("[INFO] Skipping UPX compression on macOS due to framework compatibility issues")
    else:
        cmd.insert(3, "--onefile")  # Single executable file for other platforms
        # Add UPX compression for other platforms if available
        if shutil.which("upx"):
            cmd.insert(4, "--enable-plugin=upx")
            print("[INFO] UPX compression enabled")
        else:
            print("[WARN] UPX not found, skipping compression")
    
    print("[BUILD] Building plua with Nuitka...")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, cwd=scripts_dir)
        
        # Find the created executable
        dist_dir = scripts_dir / "dist"
        
        if sys.platform == "darwin":
            # On macOS with --mode=app, Nuitka creates an .app bundle
            # The actual name is based on the input file, not --output-filename
            executable_path = dist_dir / "build_main_standalone.app" / "Contents" / "MacOS" / "plua"
            app_bundle_path = dist_dir / "build_main_standalone.app"
        else:
            # On other platforms with --onefile, creates a single executable
            executable_name = "plua.exe" if sys.platform == "win32" else "plua"
            executable_path = dist_dir / executable_name
            app_bundle_path = None
        
        if executable_path.exists():
            size_mb = executable_path.stat().st_size / (1024 * 1024)
            print("[OK] Build successful!")
            if app_bundle_path:
                print(f"  App Bundle: {app_bundle_path}")
                print(f"  Executable: {executable_path}")
                print(f"  Size: {size_mb:.1f} MB")
                print(f"  Test with: {executable_path} --help")
                print(f"  Or run app: open {app_bundle_path}")
            else:
                print(f"  Executable: {executable_path}")
                print(f"  Size: {size_mb:.1f} MB")
                print(f"  Test with: {executable_path} --help")
        else:
            print("[ERROR] Executable not found in expected location")
            if app_bundle_path:
                print(f"  Expected app bundle: {app_bundle_path}")
            print(f"  Expected executable: {executable_path}")
            
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Build failed with exit code {e.returncode}")
        sys.exit(1)


if __name__ == "__main__":
    build_nuitka()
