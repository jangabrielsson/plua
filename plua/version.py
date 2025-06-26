import os
import sys

try:
    import toml
except ImportError:
    # Fallback if toml is not available
    toml = None


def get_version():
    # If toml is not available, return a default version
    if toml is None:
        return "1.0.0"
    
    # Detect if running in a PyInstaller bundle
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
        pyproject = os.path.join(base_path, 'pyproject.toml')
    else:
        # In development mode, look for pyproject.toml in the parent directory
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        pyproject = os.path.join(base_path, 'pyproject.toml')

    try:
        with open(pyproject, 'r') as f:
            data = toml.load(f)
        return data['project']['version']
    except (FileNotFoundError, KeyError, Exception):
        # Fallback if file is not found or has unexpected format
        return "1.0.0"


__version__ = get_version()
