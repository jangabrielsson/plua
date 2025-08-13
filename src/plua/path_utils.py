"""
Path utilities for PLua.

This module provides functions to locate static files and resources
used by the PLua framework.
"""

import os


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
    # Get the directory containing this module
    module_dir = os.path.dirname(__file__)
    
    # Construct path to static file
    static_path = os.path.join(module_dir, "static", filename)
    
    # Verify the file exists
    if not os.path.exists(static_path):
        raise FileNotFoundError(f"Static file not found: {filename}")
    
    return static_path
