#!/usr/bin/env python3
"""
EPLua Interactive REPL Demo

This script demonstrates how to use the new interactive REPL functionality.
Run this script to start an interactive EPLua session.
"""


def main():
    """Demo the interactive REPL"""
    print("🚀 EPLua Interactive REPL Demo")
    print("=" * 40)
    print()
    print("This demo will:")
    print("1. Start the EPLua engine with telnet server")
    print("2. Launch the interactive REPL client")
    print("3. Allow you to execute Lua commands interactively")
    print()
    print("Available commands in the REPL:")
    print("  help     - Show help information")
    print("  clear    - Clear the screen")
    print("  exit     - Exit the REPL")
    print("  quit     - Exit the REPL")
    print()
    print("Lua examples you can try:")
    print("  print('Hello, World!')")
    print("  local x = 10; print(x * 2)")
    print("  _PY.get_time()")
    print("  timer.setTimeout(1000, function() print('Timeout!') end)")
    print()
    
    input("Press Enter to start the interactive REPL...")
    
    # Start the interactive REPL
    try:
        # Import and run the REPL
        from src.eplua.cli import run_interactive_repl
        run_interactive_repl()
    except KeyboardInterrupt:
        print("\n👋 Demo terminated by user")
    except Exception as e:
        print(f"❌ Demo error: {e}")


if __name__ == "__main__":
    main() 