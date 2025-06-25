#!/usr/bin/env python3
"""
Simple wrapper to run PLua with uv
"""
import subprocess
import sys
import os


def main():
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Build the command
    cmd = ["uv", "run", "python", os.path.join(script_dir, "plua.py")] + sys.argv[1:]

    print(f"Running: {' '.join(cmd)}", file=sys.stderr)

    # Run the command
    result = subprocess.run(cmd, cwd=script_dir)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
