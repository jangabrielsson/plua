#!/usr/bin/env python3
"""
Simplified Nuitka build script optimized for CI environments.

This version has fewer dependencies and more conservative settings 
to avoid CI build failures.
"""

import sys
import subprocess
import shutil
from pathlib import Path
import os

def build_nuitka_ci():
    """Build plua using Nuitka with CI-friendly settings"""
    
    project_root = Path(__file__).parent
    scripts_dir = project_root
    actual_project_root = project_root.parent
    src_path = actual_project_root / "src"
    
    # Ensure Nuitka is available
    try:
        result = subprocess.run([sys.executable, "-m", "nuitka", "--version"], 
                              capture_output=True, text=True, check=True)
        print(f"[OK] Nuitka is available: {result.stdout.strip()}")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Nuitka command failed: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("[ERROR] Python or Nuitka command not found")
        sys.exit(1)
    
    # Build command with minimal, conservative settings
    cmd = [
        sys.executable, "-m", "nuitka",
        "--assume-yes-for-downloads",
        "--follow-stdlib",
        
        # Include essential packages only
        "--include-package=plua",
        "--include-package=lupa",
        "--include-package=aiohttp",
        "--include-package=fastapi",
        "--include-package=uvicorn",
        
        # Output settings
        "--output-dir=dist",
        "--output-filename=plua",
        
        # Platform-specific mode
    ]
    
    # Add platform-specific settings
    if sys.platform == "darwin":
        cmd.extend(["--mode=app", "--macos-app-icon=none"])
        print("[INFO] macOS: Building as app bundle")
    else:
        cmd.append("--onefile")
        print(f"[INFO] {sys.platform}: Building as single executable")
    
    # Add the main script
    cmd.append("build_main_standalone.py")
    
    print("[BUILD] Building plua with Nuitka (CI mode)...")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        # Run with visible output for CI debugging
        result = subprocess.run(cmd, check=True, cwd=scripts_dir)
        
        # Find the created executable
        dist_dir = scripts_dir / "dist"
        
        if sys.platform == "darwin":
            executable_path = dist_dir / "build_main_standalone.app" / "Contents" / "MacOS" / "plua"
            app_bundle_path = dist_dir / "build_main_standalone.app"
        else:
            executable_name = "plua.exe" if sys.platform == "win32" else "plua"
            executable_path = dist_dir / executable_name
            app_bundle_path = None
        
        if executable_path.exists():
            size_mb = executable_path.stat().st_size / (1024 * 1024)
            print("[OK] CI Build successful!")
            if app_bundle_path:
                print(f"  App Bundle: {app_bundle_path}")
            print(f"  Executable: {executable_path}")
            print(f"  Size: {size_mb:.1f} MB")
        else:
            print("[ERROR] Executable not found in expected location")
            print(f"  Expected: {executable_path}")
            # List what was actually created
            if dist_dir.exists():
                print("  Contents of dist directory:")
                for item in dist_dir.iterdir():
                    print(f"    {item}")
            sys.exit(1)
            
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Build failed with exit code {e.returncode}")
        sys.exit(1)


if __name__ == "__main__":
    build_nuitka_ci()
