import os
import sys
import toml


def get_version():
    # Detect if running in a PyInstaller bundle
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    pyproject = os.path.join(base_path, 'pyproject.toml')
    with open(pyproject, 'r') as f:
        data = toml.load(f)
    return data['project']['version']


__version__ = get_version() 