"""
Demo script to showcase Rich console capabilities in PLua
"""

# Test all the styled print functions
from src.plua.console import console, print_info, print_warning, print_error, print_success, print_highlight

print("=== PLua Rich Console Demo ===")
print()

# Test basic Rich markup
console.print("Welcome to [bold cyan]PLua[/bold cyan] with [bold green]Rich[/bold green] support! :rocket:")
print()

# Test themed styles
print_info("This is an info message with cyan styling")
print_warning("This is a warning message with yellow styling") 
print_error("This is an error message with bold red styling")
print_success("This is a success message with bold green styling")
print_highlight("This is a highlighted message with bold magenta styling")
print()

# Test Rich features
console.print("Rich supports [bold]bold[/bold], [italic]italic[/italic], [underline]underline[/underline]")
console.print("Colors: [red]red[/red], [green]green[/green], [blue]blue[/blue], [yellow]yellow[/yellow]")
console.print("Emojis work too: :thumbs_up: :fire: :star: :rocket:")
print()

# Test markup with variables
version = "1.2.21"
console.print(f"PLua version [version]{version}[/version] is running on [python]Python[/python]")
