"""
Interactive REPL for plua2
Provides a Lua-like interactive prompt with access to plua2 features
"""

import asyncio
import sys
import traceback
from typing import Optional
from .runtime import LuaAsyncRuntime


class Plua2REPL:
    """Interactive        # Give the API server a moment to start
        await asyncio.sleep(0.5)L for plua2 with async support"""
    
    def __init__(self, debug: bool = False):
        self.runtime = LuaAsyncRuntime()
        self.debug = debug
        self.running = True
        self.repl_task = None
        
    async def initialize(self):
        """Initialize the runtime and start callback loop"""
        self.runtime.initialize_lua()
        await self.runtime.start_callback_loop()
        
        # Set debug mode
        if self.debug:
            self.runtime.interpreter.set_debug_mode(True)
    
    def show_welcome(self):
        """Show welcome message for the REPL"""
        from . import __version__
        import lupa
        
        try:
            lua = lupa.LuaRuntime()
            lua_version = lua.eval('_VERSION')
        except Exception:
            lua_version = "Lua (version unknown)"
            
        print(f"Plua2 v{__version__} Interactive REPL")
        print(f"Running {lua_version} with async runtime support")
        print()
        print("Quick start:")
        print("  help()                           - Show available commands")
        print("  print('Hello, plua2!')           - Basic Lua")
        print("  json.encode({name='test'})       - JSON encoding")
        print("  net.HTTPClient()                 - Create HTTP client")
        print("  setTimeout(function() print('Hi!') end, 2000) - Async timer")
        print()
        print("Type 'exit()' or press Ctrl+D to quit")
        print()
    
    def show_help(self):
        """Show REPL help"""
        print("Plua2 REPL Commands:")
        print("  exit()          - Exit the REPL")
        print("  help()          - Show this help")
        print("  state()         - Show runtime state")
        print("  clear()         - Clear screen")
        print("  debug(true/false) - Toggle debug mode")
        print()
        print("Lua functions available:")
        print("  setTimeout(fn, ms) - Schedule function execution")
        print("  clearTimeout(id)   - Cancel scheduled timer")
        print("  json.encode(obj)   - Convert to JSON")
        print("  json.decode(str)   - Parse JSON")
        print("  net.HTTPClient()   - Create HTTP client")
        print("  net.HTTPServer()   - Create HTTP server")
        print("  _PY.*             - Python integration functions")
        print()
        print("Tips:")
        print("  - Use Ctrl+C to cancel input, Ctrl+D to exit")
        print("  - Variables persist throughout the session") 
        print("  - Async operations run in the background")
        print()
    
    def show_state(self):
        """Show current runtime state"""
        try:
            state = self.runtime.interpreter.get_runtime_state()
            print(f"Runtime state:")
            print(f"  Active timers: {state['active_timers']}")
            print(f"  Pending callbacks: {state['pending_callbacks']}")
            print(f"  Total tasks: {state['total_tasks']}")
            
            # Get asyncio task info
            tasks = [t for t in asyncio.all_tasks() if not t.done()]
            print(f"  Asyncio tasks: {len(tasks)}")
            for task in tasks:
                name = task.get_name() if hasattr(task, 'get_name') else "unnamed"
                print(f"    - {name}")
        except Exception as e:
            print(f"Error getting state: {e}")
    
    def execute_lua_statement(self, statement: str) -> bool:
        """
        Execute a Lua statement and return True if successful
        Handles special REPL commands
        """
        statement = statement.strip()
        
        if not statement:
            return True
            
        # Handle special REPL commands
        if statement in ['exit()', 'quit()']:
            self.running = False
            return True
        elif statement in ['help()']:
            self.show_help()
            return True
        elif statement in ['state()']:
            self.show_state()
            return True
        elif statement in ['clear()']:
            # Clear screen
            print('\033[2J\033[H', end='')
            return True
        elif statement.startswith('debug('):
            try:
                # Simple debug toggle
                if 'true' in statement:
                    self.debug = True
                    self.runtime.interpreter.set_debug_mode(True)
                    print("Debug mode enabled")
                elif 'false' in statement:
                    self.debug = False
                    self.runtime.interpreter.set_debug_mode(False)
                    print("Debug mode disabled")
                else:
                    print(f"Debug mode: {'enabled' if self.debug else 'disabled'}")
            except Exception as e:
                print(f"Error toggling debug: {e}")
            return True
        
        # Try to execute as Lua code
        try:
            lua = self.runtime.interpreter.get_lua_runtime()
            if not lua:
                print("Error: Lua runtime not available")
                return False
                
            # Try to execute as expression first (for immediate results)
            try:
                # Wrap in return to get the result
                expr_code = f"return {statement}"
                result = lua.execute(expr_code)
                if result is not None:
                    print(result)
            except:
                # If expression fails, try as statement
                lua.execute(statement)
            
            return True
            
        except Exception as e:
            print(f"Lua error: {e}")
            if self.debug:
                traceback.print_exc()
            return False
    
    async def read_input(self) -> Optional[str]:
        """Read input from user asynchronously"""
        # Use asyncio to read input without blocking the event loop
        loop = asyncio.get_event_loop()
        try:
            # Run input() in a thread pool to avoid blocking
            line = await loop.run_in_executor(None, input, "plua2> ")
            return line
        except EOFError:
            return None
        except KeyboardInterrupt:
            print()  # New line after ^C
            return ""  # Empty string to continue
    
    async def repl_loop(self):
        """Main REPL loop"""
        while self.running:
            try:
                line = await self.read_input()
                
                if line is None:  # EOF (Ctrl+D)
                    print("\nGoodbye!")
                    break
                    
                if line == "":  # Empty line or Ctrl+C
                    continue
                
                # Execute the statement
                self.execute_lua_statement(line)
                
            except KeyboardInterrupt:
                print("\nUse exit() or Ctrl+D to quit")
                continue
            except Exception as e:
                print(f"REPL error: {e}")
                if self.debug:
                    traceback.print_exc()
    
    async def start(self):
        """Start the REPL"""
        try:
            # Initialize runtime
            await self.initialize()
            
            # Show welcome message
            self.show_welcome()
            
            # Start REPL loop
            self.repl_task = asyncio.create_task(self.repl_loop(), name="repl_loop")
            await self.repl_task
            
        finally:
            # Clean shutdown
            self.runtime.stop()


async def run_repl(debug: bool = False):
    """Main function to run the REPL"""
    # Name the main task
    current_task = asyncio.current_task()
    if current_task:
        current_task.set_name("repl_main")
    
    repl = Plua2REPL(debug)
    await repl.start()


async def run_repl_with_api(debug: bool = False, api_config: dict = None):
    """Main function to run the REPL with API server"""
    # Name the main task
    current_task = asyncio.current_task()
    if current_task:
        current_task.set_name("repl_api_main")
    
    repl = Plua2REPL(debug)
    
    # Start API server if requested
    api_task = None
    if api_config:
        from .api_server import PlUA2APIServer
        
        print(f"API server on {api_config['host']}:{api_config['port']}")
        api_server = PlUA2APIServer(repl.runtime, api_config['host'], api_config['port'])
        
        # Connect the broadcast UI update hook
        def broadcast_hook(qa_id):
            """Wrapper to create async task for broadcasting"""
            if api_server:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # Create a task to run the async broadcast function
                    asyncio.create_task(api_server.broadcast_ui_update(qa_id))
        
        # Set the broadcast hook in the interpreter
        repl.runtime.interpreter.set_broadcast_ui_update_hook(broadcast_hook)
        
        # Start API server in background
        api_task = asyncio.create_task(api_server.start_server(), name="api_server")
        
        # Give the API server a moment to start
        await asyncio.sleep(0.5)
        print()
    
    try:
        await repl.start()
    finally:
        # Clean up API server
        if api_task:
            api_task.cancel()
            try:
                await api_task
            except asyncio.CancelledError:
                pass
