#!/usr/bin/env python3
"""
Standalone entry point for plua Nuitka build
"""
import sys
import os

# Add src directory to path so we can import plua modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from plua.main import main

if __name__ == "__main__":
    main()
