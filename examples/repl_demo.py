#!/usr/bin/env python3
"""
PLua Interactive REPL Demo

This script demonstrates how to use PLua's interactive REPL functionality.
PLua provides two interactive modes:
1. Interactive mode (-i): Direct stdin/stdout REPL with prompt_toolkit
2. Telnet mode (--telnet): Multi-session telnet server for remote access
"""

import subprocess
import sys
import time
from pathlib import Path


def main():
    """Demo the interactive REPL"""
    print("🚀 PLua Interactive REPL Demo")
    print("=" * 40)
    print()
    print("PLua provides two interactive modes:")
    print()
    print("1. Interactive Mode (-i):")
    print("   - Direct stdin/stdout REPL")
    print("   - Rich prompt_toolkit interface")
    print("   - Command history and completion")
    print("   - Usage: plua -i")
    print()
    print("2. Telnet Mode (--telnet):")
    print("   - Multi-session telnet server")
    print("   - Remote access via telnet clients")
    print("   - Usage: plua --telnet")
    print()
    print("Available commands in both REPLs:")
    print("  help     - Show help information")
    print("  exit     - Exit the REPL")
    print()
    print("Lua examples you can try:")
    print("  print('Hello, World!')")
    print("  local x = 10; print(x * 2)")
    print("  _PY.get_time()")
    print("  timer.setTimeout(1000, function() print('Timeout!') end)")
    print()
    
    # Determine plua executable path
    project_root = Path(__file__).parent.parent
    plua_script = project_root / "run.sh"
    
    if not plua_script.exists():
        print("❌ PLua run script not found. Please run from project root.")
        return
    
    print("Choose demo mode:")
    print("1. Interactive mode (-i)")
    print("2. Telnet mode (--telnet)")
    print("0. Exit")
    
    try:
        choice = input("\nEnter choice (0-2): ").strip()
        
        if choice == "0":
            print("👋 Demo cancelled")
            return
        elif choice == "1":
            print("\n🚀 Starting PLua in interactive mode...")
            print("Type 'exit' to quit the REPL")
            print("-" * 40)
            subprocess.run([str(plua_script), "-i"], cwd=project_root)
        elif choice == "2":
            print("\n🚀 Starting PLua telnet server...")
            print("Connect with: telnet localhost 8023")
            print("Press Ctrl+C to stop the server")
            print("-" * 40)
            try:
                subprocess.run([str(plua_script), "--telnet"], cwd=project_root)
            except KeyboardInterrupt:
                print("\n🛑 Telnet server stopped")
        else:
            print("❌ Invalid choice")
            
    except KeyboardInterrupt:
        print("\n👋 Demo terminated by user")
    except Exception as e:
        print(f"❌ Demo error: {e}")


if __name__ == "__main__":
    main() 