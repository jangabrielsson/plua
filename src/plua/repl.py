#!/usr/bin/env python3
"""
EPLua REPL Client

A command-line REPL client that connects to the EPLua telnet server
and provides a rich interactive experience with history, completion,
and proper input handling using prompt_toolkit.
"""

import socket
import threading
import time
import os
from pathlib import Path

try:
    from prompt_toolkit import PromptSession
    from prompt_toolkit.history import FileHistory
    from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
    from prompt_toolkit.completion import WordCompleter
    from prompt_toolkit.styles import Style
    PROMPT_TOOLKIT_AVAILABLE = True
except ImportError:
    PROMPT_TOOLKIT_AVAILABLE = False
    print("Warning: prompt_toolkit not available, falling back to basic input")


class EPLuaREPL:
    """Interactive REPL client for EPLua with enhanced UI"""
    
    def __init__(self, host: str = 'localhost', port: int = 8023):
        self.host = host
        self.port = port
        self.socket = None
        self.running = False
        self.history_file = Path.home() / '.eplua_history'
        self.output_buffer = []
        self.setup_prompt_toolkit()
    
    def setup_prompt_toolkit(self):
        """Setup prompt_toolkit session with history and completion"""
        if not PROMPT_TOOLKIT_AVAILABLE:
            return
        
        # Create word completer for common Lua commands
        lua_completer = WordCompleter([
            'print', 'local', 'function', 'if', 'then', 'else', 'end',
            'for', 'while', 'do', 'repeat', 'until', 'break', 'return',
            'true', 'false', 'nil', 'and', 'or', 'not', 'in',
            '_PY.get_time', '_PY.sleep', 'timer.setTimeout', 'timer.setInterval',
            'exit', 'quit', 'help', 'clear'
        ], ignore_case=True)
        
        # Setup history
        try:
            history = FileHistory(str(self.history_file))
        except Exception:
            history = None
        
        # Create prompt session
        self.session = PromptSession(
            history=history,
            auto_suggest=AutoSuggestFromHistory(),
            completer=lua_completer,
            complete_while_typing=True,
            enable_history_search=True,
            complete_in_thread=True,
        )
        
        # Setup styling
        self.style = Style.from_dict({
            'prompt': 'ansicyan bold',
            'output': 'ansigreen',
            'error': 'ansired',
            'info': 'ansiyellow',
        })
    
    def connect(self) -> bool:
        """Connect to the EPLua telnet server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            return True
        except Exception as e:
            print(f"Failed to connect to {self.host}:{self.port}: {e}")
            return False
    
    def receive_messages(self):
        """Receive and display messages from the server"""
        while self.running and self.socket:
            try:
                data = self.socket.recv(1024)
                if not data:
                    break
                message = data.decode('utf-8')
                if message.strip():
                    # Store output for display
                    self.output_buffer.append(message.rstrip())
                    # Print output without extra newlines
                    # For prompt_toolkit, we need to be careful about newlines
                    if PROMPT_TOOLKIT_AVAILABLE:
                        # Use sys.stdout directly to avoid prompt_toolkit interference
                        import sys
                        sys.stdout.write(message)
                        sys.stdout.flush()
                    else:
                        print(message, end='', flush=True)
            except (socket.error, OSError) as e:
                # Socket errors are expected when connection is closed
                if self.running:
                    print(f"\nConnection closed: {e}")
                break
            except Exception as e:
                print(f"[DEBUG] Unexpected error: {e}")
                break
        
        if self.running:
            print("\nConnection lost")
            self.running = False
    
    def send_command(self, command: str):
        """Send a command to the server"""
        if self.socket and self.running:
            try:
                self.socket.send(f"{command}\n".encode('utf-8'))
            except Exception as e:
                print(f"Error sending command: {e}")
                self.running = False
    
    def get_prompt_text(self) -> str:
        """Get the prompt text with optional status indicators"""
        status = "🟢" if self.running and self.socket else "🔴"
        return f"{status} eplua> "
    
    def run(self):
        """Run the interactive REPL with enhanced UI"""
        if not self.connect():
            return
        
        self.running = True
        
        # Start receiver thread
        receiver = threading.Thread(target=self.receive_messages, daemon=True)
        receiver.start()
        
        # Wait for welcome message from server
        time.sleep(0.5)
        
        # Server already sends welcome message, so we just show additional info
        print("Type 'help' for available commands")
        print("Use Ctrl+C to interrupt, Ctrl+D to exit\n")
        
        try:
            while self.running:
                try:
                    # Get input with enhanced prompt
                    if PROMPT_TOOLKIT_AVAILABLE:
                        command = self.session.prompt(
                            self.get_prompt_text(),
                            style=self.style
                        )
                    else:
                        command = input(self.get_prompt_text())
                    
                    if not command.strip():
                        continue
                    
                    if command.lower() in ['exit', 'quit']:
                        # Send exit command that will trigger full shutdown
                        self.send_command("exit")
                        break
                    
                    if command.lower() == 'help':
                        self.show_help()
                        continue
                    
                    if command.lower() == 'clear':
                        os.system('clear' if os.name != 'nt' else 'cls')
                        continue
                    
                    if command.lower() == 'history':
                        self.show_history()
                        continue
                    
                    # Send command to server
                    self.send_command(command)
                    
                except EOFError:
                    break
                except KeyboardInterrupt:
                    print("\nUse 'exit' or 'quit' to disconnect, or continue typing...")
                    continue
                    
        except Exception as e:
            print(f"Error: {e}")
        finally:
            self.cleanup()
    
    def show_help(self):
        """Show help information"""
        help_text = """
Available commands:
  help     - Show this help message
  clear    - Clear the screen
  history  - Show command history
  exit     - Exit the REPL
  quit     - Exit the REPL

Lua commands:
  Any valid Lua code can be executed directly
  Examples:
    print("Hello, World!")
    local x = 10
    print(x * 2)
    _PY.get_time()
    timer.setTimeout(1000, function() print("Timeout!") end)

Features:
  - Command history (use ↑/↓ arrows)
  - Auto-completion (Tab key)
  - Multi-line editing
  - Syntax highlighting
        """
        print(help_text)
    
    def show_history(self):
        """Show recent command history"""
        if PROMPT_TOOLKIT_AVAILABLE and hasattr(self.session, 'history'):
            print("\nRecent commands:")
            try:
                # Get recent history items
                history_items = list(self.session.history.load_history_strings())
                for i, item in enumerate(history_items[-10:], 1):  # Last 10 items
                    print(f"  {i:2d}. {item}")
            except Exception:
                print("  History not available")
        else:
            print("History not available")
        print()
    
    def cleanup(self):
        """Clean up resources"""
        self.running = False
        if self.socket:
            try:
                self.socket.close()
            except Exception:
                pass
        print("\n👋 Disconnected from EPLua")


def main():
    """Main entry point for the REPL client"""
    import argparse
    
    parser = argparse.ArgumentParser(description="EPLua Interactive REPL Client")
    parser.add_argument("--host", default="localhost", help="Telnet server host (default: localhost)")
    parser.add_argument("--port", type=int, default=8023, help="Telnet server port (default: 8023)")
    
    args = parser.parse_args()
    
    if not PROMPT_TOOLKIT_AVAILABLE:
        print("Note: Install prompt_toolkit for enhanced features:")
        print("  pip install prompt_toolkit")
        print()
    
    repl = EPLuaREPL(args.host, args.port)
    repl.run()


if __name__ == "__main__":
    main() 