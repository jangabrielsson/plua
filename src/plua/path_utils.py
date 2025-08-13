"""
Path utilities for plua - handles resource paths in both development and packaged environments
"""

import os
from pathlib import Path
from typing import Optional


def get_static_path() -> Path:
    """
    Get the path to static files, handling both development and packaged environments.
    
    Returns:
        Path to the static directory
        
    Raises:
        FileNotFoundError: If static directory cannot be found
    """
    current_dir = Path(__file__).parent.absolute()
    
    # Try different possible locations in order of preference:
    
    # 1. Package static directory (for installed package or Nuitka build)
    package_static_dir = current_dir / "static"
    if package_static_dir.exists():
        return package_static_dir
    
    # 2. Executable directory static (for Nuitka/PyInstaller builds)
    # Get the directory where the executable is located
    if hasattr(os, '_MEIPASS'):
        # PyInstaller bundle
        bundle_static = Path(os._MEIPASS) / "static"
        if bundle_static.exists():
            return bundle_static
    
    # For Nuitka, check if we're in a compiled executable
    executable_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    if str(executable_dir).endswith('.app/Contents/MacOS') or 'dist' in str(executable_dir):
        # We're likely in a Nuitka build - static should be next to the executable
        exe_static = executable_dir / "static"
        if exe_static.exists():
            return exe_static
    
    # 3. Project root static directory (for development)
    project_root = current_dir.parent.parent
    project_static_dir = project_root / "static"
    if project_static_dir.exists():
        return project_static_dir
        
    # 4. Source tree static directory (for development from src/)
    src_static_dir = current_dir / ".." / ".." / "src" / "plua" / "static"
    src_static_path = Path(src_static_dir).resolve()
    if src_static_path.exists():
        return src_static_path
    
    # If we get here, we couldn't find static files anywhere
    checked_paths = [
        package_static_dir,
        project_static_dir, 
        src_static_path
    ]
    
    if hasattr(os, '_MEIPASS'):
        checked_paths.insert(1, Path(os._MEIPASS) / "static")
    
    if str(executable_dir).endswith('.app/Contents/MacOS') or 'dist' in str(executable_dir):
        checked_paths.insert(-1, executable_dir / "static")
    
    raise FileNotFoundError(
        f"Static directory not found. Checked paths:\n" + 
        "\n".join(f"  - {path}" for path in checked_paths)
    )


def get_static_file(filename: str) -> Path:
    """
    Get the path to a specific static file.
    
    Args:
        filename: Name of the file in the static directory
        
    Returns:
        Path to the static file
        
    Raises:
        FileNotFoundError: If static directory or file cannot be found
    """
    static_dir = get_static_path()
    file_path = static_dir / filename
    
    if not file_path.exists():
        raise FileNotFoundError(f"Static file not found: {file_path}")
    
    return file_path


def get_lua_path() -> Path:
    """
    Get the path to Lua runtime files, handling both development and packaged environments.
    
    Returns:
        Path to the lua directory
        
    Raises:
        FileNotFoundError: If lua directory cannot be found
    """
    current_dir = Path(__file__).parent.absolute()
    
    # Try different possible locations:
    
    # 1. Next to executable (for Nuitka/PyInstaller builds)
    executable_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    if str(executable_dir).endswith('.app/Contents/MacOS') or 'dist' in str(executable_dir):
        exe_lua = executable_dir / "lua"
        if exe_lua.exists():
            return exe_lua
    
    # 2. PyInstaller bundle
    if hasattr(os, '_MEIPASS'):
        bundle_lua = Path(os._MEIPASS) / "lua"
        if bundle_lua.exists():
            return bundle_lua
    
    # 3. Source tree lua directory (for development)
    src_lua_dir = current_dir / ".." / ".." / "src" / "lua"
    src_lua_path = Path(src_lua_dir).resolve()
    if src_lua_path.exists():
        return src_lua_path
    
    # 4. Project root lua directory
    project_root = current_dir.parent.parent
    project_lua_dir = project_root / "lua"
    if project_lua_dir.exists():
        return project_lua_dir
    
    # If we get here, we couldn't find lua files anywhere
    checked_paths = [
        src_lua_path,
        project_lua_dir
    ]
    
    if hasattr(os, '_MEIPASS'):
        checked_paths.insert(0, Path(os._MEIPASS) / "lua")
    
    if str(executable_dir).endswith('.app/Contents/MacOS') or 'dist' in str(executable_dir):
        checked_paths.insert(0, executable_dir / "lua")
    
    raise FileNotFoundError(
        f"Lua directory not found. Checked paths:\n" + 
        "\n".join(f"  - {path}" for path in checked_paths)
    )
