#!/usr/bin/env python3
"""
Test environment detection logic
"""

import sys
import os
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def test_environment_detection():
    """Test the environment detection function with different argv scenarios"""
    
    # Import the function from CLI module
    from plua.cli import detect_environment
    
    # Save original argv
    original_argv = sys.argv[:]
    
    print("Testing environment detection...")
    
    # Test VS Code environment
    sys.argv = ["plua", "--fibaro", "test.lua", "vscode", "lua-mobdebug"]
    env = detect_environment()
    print(f"VS Code test: {env} (expected: vscode)")
    assert env == "vscode", f"Expected 'vscode', got '{env}'"
    
    # Test ZeroBrane environment
    sys.argv = ["plua", "test.lua", "io.stdout:setvbuf('no')"]
    env = detect_environment()
    print(f"ZeroBrane test: {env} (expected: zerobrane)")
    assert env == "zerobrane", f"Expected 'zerobrane', got '{env}'"
    
    # Test terminal environment (default)
    sys.argv = ["plua", "--fibaro", "test.lua"]
    env = detect_environment()
    print(f"Terminal test: {env} (expected: terminal)")
    assert env == "terminal", f"Expected 'terminal', got '{env}'"
    
    # Test with both VS Code markers
    sys.argv = ["plua", "--fibaro", "test.lua", "--debug", "vscode", "lua-mobdebug", "extra-args"]
    env = detect_environment()
    print(f"VS Code with extra args: {env} (expected: vscode)")
    assert env == "vscode", f"Expected 'vscode', got '{env}'"
    
    # Test with ZeroBrane marker in middle
    sys.argv = ["plua", "io.stdout:setvbuf('no')", "test.lua"]
    env = detect_environment()
    print(f"ZeroBrane with args: {env} (expected: zerobrane)")
    assert env == "zerobrane", f"Expected 'zerobrane', got '{env}'"
    
    # Test priority (VS Code should win over ZeroBrane if both present)
    sys.argv = ["plua", "vscode", "lua-mobdebug", "io.stdout:setvbuf('no')", "test.lua"]
    env = detect_environment()
    print(f"Priority test (VS Code + ZeroBrane): {env} (expected: vscode)")
    assert env == "vscode", f"Expected 'vscode', got '{env}'"
    
    # Restore original argv
    sys.argv = original_argv
    
    print("✅ All environment detection tests passed!")

if __name__ == "__main__":
    test_environment_detection()
