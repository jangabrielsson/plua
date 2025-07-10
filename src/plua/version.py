import os
import sys

try:
    import importlib.metadata
    METADATA_AVAILABLE = True
except ImportError:
    METADATA_AVAILABLE = False

try:
    import toml
    TOML_AVAILABLE = True
except ImportError:
    TOML_AVAILABLE = False


def get_version():
    # First, try to get version from installed package metadata
    if METADATA_AVAILABLE:
        try:
            return importlib.metadata.version("plua")
        except importlib.metadata.PackageNotFoundError:
            pass
    
    # If toml is not available, return a default version
    if not TOML_AVAILABLE:
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
        # Only show warning in development mode, not in installed package
        if not METADATA_AVAILABLE:
            print(f"Warning: Could not read version from pyproject.toml: {e}", file=sys.stderr)
        return "1.0.2"


__version__ = get_version()
