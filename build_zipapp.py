#!/usr/bin/env python3
"""
Build script for creating a portable plua using zipapp with embedded Python

This creates the fastest-starting solution by avoiding the overhead of 
bundled executables.

Prerequisites:
    - Download Python embeddable package from python.org
    - Or use system Python for development

Usage:
    python build_zipapp.py

This creates a lightweight, fast-starting solution.
"""

import os
import sys
import zipapp
import shutil
import subprocess
from pathlib import Path
import tempfile

def create_zipapp():
    """Create a zipapp version of plua"""
    
    project_root = Path(__file__).parent
    src_path = project_root / "src"
    static_path = project_root / "static"
    lua_path = src_path / "lua"
    
    # Create output directory
    dist_dir = project_root / "dist_zipapp"
    dist_dir.mkdir(exist_ok=True)
    
    # Create temporary build directory
    with tempfile.TemporaryDirectory() as temp_dir:
        build_path = Path(temp_dir) / "plua_build"
        build_path.mkdir()
        
        print("📦 Copying source files...")
        
        # Copy plua source
        plua_build = build_path / "plua"
        shutil.copytree(src_path / "plua", plua_build)
        
        # Copy Lua files
        lua_build = build_path / "lua"
        shutil.copytree(lua_path, lua_build)
        
        # Copy static files
        static_build = build_path / "static" 
        shutil.copytree(static_path, static_build)
        
        # Create __main__.py for zipapp entry point
        main_content = '''#!/usr/bin/env python3
"""Entry point for plua zipapp"""

if __name__ == "__main__":
    from plua.main import main
    main()
'''
        
        (build_path / "__main__.py").write_text(main_content)
        
        # Install dependencies to build directory
        print("📦 Installing dependencies...")
        
        requirements = [
            "lupa>=2.0",
            "aiohttp>=3.8.0", 
            "fastapi>=0.104.0",
            "uvicorn[standard]>=0.24.0",
            "psutil>=5.9.0",
            "requests>=2.28.0",
            "httpx>=0.24.0",
        ]
        
        for req in requirements:
            cmd = [
                sys.executable, "-m", "pip", "install",
                "--target", str(build_path),
                "--no-deps",  # We'll handle dependencies manually
                req
            ]
            
            try:
                subprocess.run(cmd, check=True, capture_output=True)
                print(f"  ✓ Installed {req}")
            except subprocess.CalledProcessError as e:
                print(f"  ⚠️ Failed to install {req}: {e}")
        
        # Create the zipapp
        zipapp_path = dist_dir / "plua.pyz"
        print(f"🔨 Creating zipapp: {zipapp_path}")
        
        zipapp.create_archive(
            source=build_path,
            target=zipapp_path,
            interpreter="/usr/bin/env python3",
            main="__main__:main" if hasattr(zipapp, 'main') else None,
            compressed=True
        )
        
        # Make it executable
        zipapp_path.chmod(0o755)
        
        size_mb = zipapp_path.stat().st_size / (1024 * 1024)
        print(f"✓ Zipapp created successfully!")
        print(f"  File: {zipapp_path}")
        print(f"  Size: {size_mb:.1f} MB")
        print(f"  Test with: {zipapp_path} --help")
        print(f"  Or: python3 {zipapp_path} --help")

def create_portable_bundle():
    """Create a fully portable bundle with embedded Python"""
    
    print("🔧 Creating portable bundle with embedded Python...")
    print("   Download Python embeddable from: https://www.python.org/downloads/windows/")
    print("   Extract and place python.exe in the same directory as plua.pyz")
    
    project_root = Path(__file__).parent
    dist_dir = project_root / "dist_zipapp"
    
    # Create a simple launcher script
    launcher_content = '''#!/usr/bin/env python3
"""
Portable launcher for plua

For fully portable deployment:
1. Download Python embeddable package
2. Extract python.exe to same directory as this script
3. Run: ./python plua.pyz
"""

import sys
import os
from pathlib import Path

def main():
    script_dir = Path(__file__).parent
    pyz_file = script_dir / "plua.pyz"
    
    if not pyz_file.exists():
        print(f"Error: {pyz_file} not found")
        sys.exit(1)
    
    # Try to find python executable
    python_candidates = [
        script_dir / "python.exe",      # Windows embedded
        script_dir / "python3",         # Unix embedded  
        script_dir / "python",          # Generic
        "python3",                      # System Python
        "python",                       # System Python
    ]
    
    for python_exe in python_candidates:
        if isinstance(python_exe, Path):
            if python_exe.exists():
                os.execv(str(python_exe), [str(python_exe), str(pyz_file)] + sys.argv[1:])
        else:
            import shutil
            if shutil.which(python_exe):
                os.execvp(python_exe, [python_exe, str(pyz_file)] + sys.argv[1:])
    
    print("Error: No Python executable found")
    print("Download Python embeddable and place python.exe in this directory")
    sys.exit(1)

if __name__ == "__main__":
    main()
'''
    
    launcher_path = dist_dir / "plua_launcher.py"
    launcher_path.write_text(launcher_content)
    launcher_path.chmod(0o755)
    
    print(f"✓ Portable launcher created: {launcher_path}")

if __name__ == "__main__":
    create_zipapp()
    create_portable_bundle()
