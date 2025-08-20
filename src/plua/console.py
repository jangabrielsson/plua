"""
Global Rich Console for PLua

This module provides a global Rich Console instance that can be imported
and used throughout the PLua application for consistent terminal output
formatting, colors, and styling.

The console automatically detects terminal capabilities and adjusts output
accordingly, making it platform-portable across different operating systems
and terminal emulators.
"""

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

# Create the global console instance
# This console will automatically detect terminal capabilities
# and provide cross-platform compatible output
console = Console(
    theme=plua_theme,
    highlight=True,  # Enable automatic syntax highlighting
    emoji=True,      # Enable emoji support
    markup=True,     # Enable Rich markup syntax
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

# Export the console for direct use
__all__ = [
    "console", 
    "print_info", 
    "print_warning", 
    "print_error", 
    "print_success", 
    "print_highlight"
]
