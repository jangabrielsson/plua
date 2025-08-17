#!/usr/bin/env python3
"""
Build script for creating a single-file plua executable usin        # Try a different approach - be more conservative and let Nuitka auto-detect
        "--follow-stdlib",
        # Force include warnings using package directive
        "--include-package=warnings",
        # Only absolutely essential modules
        "--include-module=threading",
        "--include-module=subprocess",a

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
    pylib_path = src_path / "pylib"
    
    # Ensure Nuitka is installed
    try:
        # Test nuitka version with visible output for debugging
        result = subprocess.run([sys.executable, "-m", "nuitka", "--version"], 
                              capture_output=True, text=True, check=True)
        print("[OK] Nuitka is available")
        print(f"[DEBUG] Nuitka version: {result.stdout.split()[0]}")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Nuitka command failed: {e}")
        print(f"[DEBUG] stderr: {e.stderr}")
        sys.exit(1)
    except FileNotFoundError:
        print("[ERROR] Python or Nuitka command not found")
        sys.exit(1)
    
    # Dynamically include all Lua files
    data_file_args = []
    lua_file_count = 0
    for file in lua_path.glob("**/*"):
        if file.is_file():
            rel_path = file.relative_to(lua_path)
            data_file_args.append(f"--include-data-file={file}=lua/{rel_path}")
            lua_file_count += 1
    
    # Dynamically include all PyLib files  
    pylib_file_count = 0
    for file in pylib_path.glob("**/*"):
        if file.is_file() and file.suffix == '.py':
            rel_path = file.relative_to(pylib_path)
            data_file_args.append(f"--include-data-file={file}=pylib/{rel_path}")
            pylib_file_count += 1
    
    print(f"[INFO] Including {lua_file_count} Lua files from src/lua/")
    print(f"[INFO] Including {pylib_file_count} PyLib files from src/pylib/")
    print(f"[INFO] Including static files from {static_path}")
    
    # Find and force include the warnings module as a data file
    warnings_source = None
    try:
        import warnings
        warnings_source = warnings.__file__
        print(f"[INFO] Found warnings module at: {warnings_source}")
    except ImportError:
        print("[WARN] Could not locate warnings module for inclusion")
    
    # Build command base
    cmd_parts = [
        sys.executable, "-m", "nuitka",
        "--assume-yes-for-downloads",   # Auto-download dependencies
        "--lto=yes",                   # Link-time optimization
        f"--include-data-dir={static_path}=static",  # Web UI files
        # Lua files included individually below
        *data_file_args,
    ]
    
    # Force include warnings.py as data file for proper module availability
    if warnings_source:
        cmd_parts.append(f"--include-data-file={warnings_source}=warnings.py")
        print(f"[INFO] Force including warnings.py as data file")
    
    cmd_parts.extend([
        # Include packages that might not be auto-detected
        "--include-package=lupa",
        "--include-package=aiohttp",
        "--include-package=fastapi", 
        "--include-package=uvicorn",
        "--include-package=psutil",
        "--include-package=httpx",
        "--include-package=websockets",
        "--include-package=aiomqtt",
        "--include-package=requests",
        # Try a minimal approach - let Nuitka auto-detect most things
        "--follow-stdlib",
        # Include the plua package explicitly
        "--include-package=plua",
        "--include-package=pylib",
        "--output-dir=dist",
        "--output-filename=plua",
        "build_main_standalone.py"
    ])
    
    cmd = cmd_parts
    
    # Add tomllib/tomli conditionally based on Python version
    if sys.version_info >= (3, 11):
        # Python 3.11+ has built-in tomllib, but it might not be auto-detected
        cmd.insert(-1, "--include-package=tomllib")
    else:
        # Older Python versions need tomli package
        try:
            import tomli
            cmd.insert(-1, "--include-package=tomli")
        except ImportError:
            print("[WARN] tomli not available for Python < 3.11, some features may not work")
    
    # Check if tomli is actually installed before including it
    try:
        import tomli
        if "--include-package=tomli" not in cmd:
            cmd.insert(-1, "--include-package=tomli")
    except ImportError:
        pass
    
    # Add platform-specific mode flags and UPX handling
    if sys.platform == "darwin":
        cmd.insert(3, "--mode=app")  # Required for Foundation framework on macOS
        cmd.insert(4, "--macos-app-icon=none")  # Disable dock icon warning
        print("[INFO] macOS detected: Using --mode=app for Foundation framework compatibility")
        # Skip UPX on macOS as it often fails with native frameworks
        print("[INFO] Skipping UPX compression on macOS due to framework compatibility issues")
    elif sys.platform == "win32":
        cmd.insert(3, "--onefile")  # Single executable file for Windows
        # Exclude multiprocessing on Windows since we use threading instead
        cmd.insert(4, "--nofollow-import-to=multiprocessing")
        print("[INFO] Windows detected: Excluding multiprocessing module (using threading instead)")
        # Add UPX compression for Windows if available
        if shutil.which("upx"):
            cmd.insert(5, "--enable-plugin=upx")
            print("[INFO] UPX compression enabled")
        else:
            print("[WARN] UPX not found, skipping compression")
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
