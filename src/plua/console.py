"""
Global Rich Console for PLua

This module provides a global Rich Console instance that can be imported
and used throughout the PLua application for consistent terminal output
formatting, colors, and styling.

The console automatically detects terminal capabilities and adjusts output
accordingly, making it platform-portable across different operating systems
and terminal emulators.
"""

import os
import sys
from rich.console import Console
from rich.theme import Theme
from rich.style import Style

# Define a custom theme for PLua with consistent colors
plua_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "bold red",
    "success": "bold green",
    "highlight": "bold magenta",
    "version": "bold cyan",
    "api": "yellow",
    "telnet": "magenta",
    "lua": "blue",
    "python": "green",
    "dim": "dim white",
    "bright": "bright_white",
})

def _should_force_colors():
    """Determine if we should force colors based on environment detection"""
    # Check for VS Code debug console
    argv_str = " ".join(sys.argv)
    if "vscode" in argv_str and "lua-mobdebug" in argv_str:
        return True
    
    # Check environment variables that indicate color support
    if os.getenv("FORCE_COLOR") or os.getenv("CLICOLOR_FORCE"):
        return True
    
    # Check if running in VS Code terminal
    if os.getenv("TERM_PROGRAM") == "vscode":
        return True
    
    return False

# Create the global console instance
# Force colors for VS Code and other environments that support ANSI but might not be detected
console = Console(
    theme=plua_theme,
    highlight=True,      # Enable automatic syntax highlighting
    emoji=True,          # Enable emoji support
    markup=True,         # Enable Rich markup syntax
    force_terminal=_should_force_colors(),  # Force terminal mode for VS Code
    color_system="truecolor" if _should_force_colors() else "auto",  # Force colors when needed
)

# Export commonly used styling functions for convenience
def print_info(message: str, **kwargs):
    """Print an info message with cyan styling"""
    console.print(message, style="info", **kwargs)

def print_warning(message: str, **kwargs):
    """Print a warning message with yellow styling"""
    console.print(message, style="warning", **kwargs)

def print_error(message: str, **kwargs):
    """Print an error message with bold red styling"""
    console.print(message, style="error", **kwargs)

def print_success(message: str, **kwargs):
    """Print a success message with bold green styling"""
    console.print(message, style="success", **kwargs)

def print_highlight(message: str, **kwargs):
    """Print a highlighted message with bold magenta styling"""
    console.print(message, style="highlight", **kwargs)

def debug_console_state():
    """Print debug information about console state - useful for troubleshooting"""
    info = {
        "is_terminal": console.is_terminal,
        "color_system": console.color_system,
        "encoding": console.encoding,
        "width": console.width,
        "height": console.height,
        "TERM": os.getenv("TERM", "Not set"),
        "TERM_PROGRAM": os.getenv("TERM_PROGRAM", "Not set"),
        "FORCE_COLOR": os.getenv("FORCE_COLOR", "Not set"),
        "CLICOLOR_FORCE": os.getenv("CLICOLOR_FORCE", "Not set"),
        "NO_COLOR": os.getenv("NO_COLOR", "Not set"),
    }
    
    print("=== Rich Console Debug Info ===")
    for key, value in info.items():
        print(f"{key}: {value}")
    print("=====================================")

def configure_console_for_environment(environment: str):
    """Reconfigure the console based on the detected environment"""
    global console
    
    force_colors = environment in ["vscode", "zerobrane"] or _should_force_colors()
    
    if force_colors:
        # Set environment variables that Rich recognizes
        os.environ["FORCE_COLOR"] = "1"
        os.environ["TERM"] = "xterm-256color"  # Ensure TERM is set for color support
        
        # Recreate console with forced colors for specific environments
        console = Console(
            theme=plua_theme,
            highlight=True,
            emoji=True,
            markup=True,
            force_terminal=True,
            color_system="truecolor",
            width=None,  # Auto-detect width
            legacy_windows=False,  # Use modern Windows terminal features
        )

# Export the console for direct use
__all__ = [
    "console", 
    "print_info", 
    "print_warning", 
    "print_error", 
    "print_success", 
    "print_highlight",
    "configure_console_for_environment",
    "debug_console_state"
]
