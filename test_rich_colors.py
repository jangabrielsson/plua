#!/usr/bin/env python3
"""
Test Rich console color detection and forcing
"""

import sys
import os

# Add the src directory to Python path
sys.path.insert(0, 'src')

from plua.console import console, configure_console_for_environment, debug_console_state

def test_console_colors():
    print("=== Rich Console Color Test ===")
    debug_console_state()
    print()
    
    # Test before configuration
    print("Before environment configuration:")
    console.print("This is a [bold cyan]test message[/bold cyan] with [red]colors[/red]")
    console.print("Version info", style="version")
    console.print("Error message", style="error")
    print()
    
    # Test VS Code environment
    print("Configuring for vscode environment:")
    configure_console_for_environment("vscode")
    debug_console_state()
    console.print("This is a [bold cyan]test message[/bold cyan] with [red]colors[/red] after vscode config")
    console.print("Version info", style="version")
    console.print("Error message", style="error")

if __name__ == "__main__":
    test_console_colors()
