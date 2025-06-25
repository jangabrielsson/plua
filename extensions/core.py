"""
Core Extensions for PLua
Provides basic functionality like timers, I/O, system, math, and utility functions.
"""

import sys
import threading
import time
from .registry import registry


# Timer management class
class TimerManager:
    """Manages setTimeout and clearTimeout functionality"""

    def __init__(self):
        self.timers = {}
        self.next_id = 1
        self.lock = threading.Lock()

    def setTimeout(self, func, ms):
        """Schedule a function to run after ms milliseconds"""
        with self.lock:
            timer_id = self.next_id
            self.next_id += 1

        def wrapped_func():
            try:
                func()
            except Exception as e:
                print(f"Timer error: {e}", file=sys.stderr)
            finally:
                with self.lock:
                    if timer_id in self.timers:
                        del self.timers[timer_id]

        timer = threading.Timer(ms / 1000.0, wrapped_func)
        self.timers[timer_id] = timer
        timer.start()

        return timer_id

    def clearTimeout(self, timer_id):
        """Cancel a timer by its ID"""
        with self.lock:
            if timer_id in self.timers:
                timer = self.timers[timer_id]
                timer.cancel()
                del self.timers[timer_id]
                return True
        return False

    def has_active_timers(self):
        """Check if there are any active timers"""
        with self.lock:
            return len(self.timers) > 0


# Global timer manager instance
timer_manager = TimerManager()


# Timer Extensions
@registry.register(description="Schedule a function to run after specified milliseconds", category="timers")
def setTimeout(func, ms):
    """Schedule a function to run after ms milliseconds"""
    return timer_manager.setTimeout(func, ms)


@registry.register(description="Cancel a timer using its reference ID", category="timers")
def clearTimeout(timer_id):
    """Cancel a timer by its ID"""
    return timer_manager.clearTimeout(timer_id)


@registry.register(description="Check if there are active timers", category="timers")
def has_active_timers():
    """Check if there are any active timers"""
    return timer_manager.has_active_timers()


# I/O Extensions
@registry.register(description="Get user input from stdin", category="io")
def input_lua(prompt=""):
    """Get user input with optional prompt"""
    return input(prompt)


@registry.register(description="Read contents of a file", category="io")
def read_file(filename):
    """Read and return the contents of a file"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading file '{filename}': {e}", file=sys.stderr)
        return None


@registry.register(description="Write content to a file", category="io")
def write_file(filename, content):
    """Write content to a file"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(str(content))
        return True
    except Exception as e:
        print(f"Error writing file '{filename}': {e}", file=sys.stderr)
        return False


# System Extensions
@registry.register(description="Get current timestamp in seconds", category="system")
def get_time():
    """Get current timestamp"""
    return time.time()


@registry.register(description="Sleep for specified seconds (non-blocking)", category="system")
def sleep(seconds):
    """Sleep for specified number of seconds (non-blocking)"""
    # Use a simple busy wait for short sleeps, setTimeout for longer ones
    if seconds < 0.1:
        # For very short sleeps, use busy wait to avoid timer overhead
        end_time = time.time() + seconds
        while time.time() < end_time:
            pass
    else:
        # For longer sleeps, use setTimeout to avoid blocking
        import threading
        event = threading.Event()
        timer_manager.setTimeout(lambda: event.set(), seconds * 1000)
        event.wait()


@registry.register(description="Get Python version information", category="system")
def get_python_version():
    """Get Python version information"""
    return f"Python {sys.version}"


# List all extensions function
@registry.register(name="list_extensions", description="List all available Python extensions", category="utility")
def list_extensions():
    """List all available extensions"""
    registry.list_extensions()
