#!/usr/bin/env python3
"""
Test runner for PLua
"""

import sys
import os
import subprocess

def main():
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up to the project root
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(script_dir)))
    
    # Change to project root
    os.chdir(project_root)
    
    # Run PLua with the CLI entry point
    cmd = ["uv", "run", "plua"] + sys.argv[1:]
    
    try:
        result = subprocess.run(cmd, check=True)
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(f"Error running PLua: {e}", file=sys.stderr)
        return e.returncode

if __name__ == "__main__":
    sys.exit(main())
