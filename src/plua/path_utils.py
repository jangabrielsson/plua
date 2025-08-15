"""
Path utilities for PLua.

This module provides functions to locate static files and resources
used by the PLua framework.
"""

import os
import sys


def get_static_file(filename: str) -> str:
    """
    Get the full path to a static file.
    
    Args:
        filename: Name of the static file to locate
        
    Returns:
        Full path to the static file
        
    Raises:
        FileNotFoundError: If the static file doesn't exist
    """
    # Find static directory - handle both development and Nuitka builds
    possible_base_dirs = [
        os.path.dirname(__file__),  # Development mode
        os.path.dirname(sys.executable),  # Nuitka build
        os.path.dirname(os.path.abspath(sys.argv[0])),  # Alternative Nuitka path
    ]
    
    for base_dir in possible_base_dirs:
        static_path = os.path.join(base_dir, "static", filename)
        if os.path.exists(static_path):
            return static_path
    
    # If not found, raise error with all tried paths
    tried_paths = [os.path.join(base_dir, "static", filename) for base_dir in possible_base_dirs]
    raise FileNotFoundError(f"Static file not found: {filename}. Tried: {tried_paths}")
