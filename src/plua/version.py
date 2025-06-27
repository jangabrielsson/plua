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
        return "1.0.2"
    
    # Detect if running in a PyInstaller bundle
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
        pyproject = os.path.join(base_path, 'pyproject.toml')
    else:
        # In development mode, look for pyproject.toml in the project root
        # Start from the current file location and go up to find pyproject.toml
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up two levels: src/plua/ -> src/ -> project root
        project_root = os.path.dirname(os.path.dirname(current_dir))
        pyproject = os.path.join(project_root, 'pyproject.toml')

    try:
        with open(pyproject, 'r', encoding='utf-8') as f:
            data = toml.load(f)
        return data['project']['version']
    except (FileNotFoundError, KeyError, Exception) as e:
        # Fallback if file is not found or has unexpected format
        print(f"Warning: Could not read version from pyproject.toml: {e}", file=sys.stderr)
        return "1.0.2"


__version__ = get_version()
