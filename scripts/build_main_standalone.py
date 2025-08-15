#!/usr/bin/env python3
"""
Standalone entry point for Nuitka-built plua executable

This file serves as the main entry point when plua is built as a standalone 
executable using Nuitka. It imports and runs the main CLI function.
"""

import sys
import os
from pathlib import Path

# Workaround for Nuitka warnings module issues
# This needs to happen VERY early, before any other imports
import sys
import builtins

# First, hijack the import mechanism to catch warnings imports
original_import = builtins.__import__

def patched_import(name, globals=None, locals=None, fromlist=(), level=0):
    """Patched import that provides warnings module stub when needed"""
    if name == 'warnings':
        # Return our stub instead of failing
        return get_warnings_stub()
    try:
        return original_import(name, globals, locals, fromlist, level)
    except ImportError as e:
        if 'warnings' in str(e):
            # If any import fails due to warnings, provide our stub
            return get_warnings_stub()
        raise

def get_warnings_stub():
    """Get or create the warnings module stub"""
    if 'warnings' in sys.modules:
        return sys.modules['warnings']
    
    class WarningsStub:
        """Comprehensive warnings module stub for Nuitka compatibility"""
        
        def warn(self, message, category=None, stacklevel=1):
            # Silently ignore warnings to prevent stderr noise
            pass
            
        def filterwarnings(self, *args, **kwargs):
            pass
            
        def simplefilter(self, *args, **kwargs):
            pass
            
        def resetwarnings(self):
            pass
            
        def showwarning(self, message, category, filename, lineno, file=None, line=None):
            pass
            
        def formatwarning(self, message, category, filename, lineno, line=None):
            return ""
        
        # Add common warning categories as mock exception classes
        UserWarning = Exception
        DeprecationWarning = Exception
        PendingDeprecationWarning = Exception
        SyntaxWarning = Exception
        RuntimeWarning = Exception
        FutureWarning = Exception
        ImportWarning = Exception
        UnicodeWarning = Exception
        BytesWarning = Exception
        ResourceWarning = Exception
    
    warnings_stub = WarningsStub()
    sys.modules['warnings'] = warnings_stub
    return warnings_stub

# Install the patch immediately
builtins.__import__ = patched_import

# Also try to preload warnings module and make it globally available
try:
    import warnings
    # Make warnings available in sys.modules if it isn't already
    if 'warnings' not in sys.modules:
        sys.modules['warnings'] = warnings
except ImportError:
    # Install our stub
    warnings_stub = get_warnings_stub()
    # Make it available globally for direct imports
    builtins.warnings = warnings_stub
    # Make it available as a global variable too
    globals()['warnings'] = warnings_stub

# Ensure the src directory is in the Python path when running as standalone
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    bundle_dir = Path(sys.executable).parent
    src_dir = bundle_dir / "src"
    if src_dir.exists():
        sys.path.insert(0, str(src_dir))
else:
    # Running from source, add the project src directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    src_dir = project_root / "src"
    if src_dir.exists():
        sys.path.insert(0, str(src_dir))

# Import and run the main CLI
if __name__ == "__main__":
    try:
        from plua.cli import main
        main()
    except ImportError as e:
        print(f"Error importing plua: {e}")
        print("Make sure plua is properly installed or built.")
        print(f"Python path: {sys.path}")
        sys.exit(1)
