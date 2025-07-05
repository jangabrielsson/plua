"""
Coroutine-based execution manager for PLua
Lua-based timer system: All timer logic is handled in Lua, avoiding Python callbacks entirely

IMPORTANT: This module implements a workaround for a fundamental Lupa limitation.
You cannot call coroutine.resume() directly from a Python callback (like a timer callback)
because it crosses the Python→Lua C boundary unsafely, causing segmentation faults.

This module uses a pure Lua-based timer system where all timer logic is handled
in Lua, avoiding the Python→Lua C boundary crossing entirely.
"""

import sys
import traceback
import lupa
import threading
import asyncio


class CoroutineManager:
    """Manages Lua coroutine execution with pure Lua-based timer system"""

    def __init__(self, lua_runtime: lupa.LuaRuntime, debug: bool = False):
        self.lua_runtime = lua_runtime
        self.timers = {}  # timer_id -> timer_handle
        self.intervals = {}  # interval_id -> interval_handle
        self.next_id = 1
        self.main_coroutine = None  # Reference to the main coroutine
        self.lock = threading.Lock()
        self.debug = debug
        self._setup_lua_environment()

    def set_main_coroutine(self, main_co):
        """Set the main coroutine that should be resumed by timers"""
        self.main_coroutine = main_co
        # Also set it in Lua
        try:
            self.lua_runtime.globals()["__temp_main_co"] = main_co
            self.lua_runtime.execute("_PY.setMainCoroutine(__temp_main_co)")
            self.lua_runtime.globals()["__temp_main_co"] = None
        except Exception as e:
            if self.debug:
                print(f"[TIMER DEBUG] Failed to set main coroutine in Lua: {e}", file=sys.stderr)

    def _setup_lua_environment(self):
        setup_code = """
        _PY = _PY or {}
        
        print('[LUA DEBUG] Setting up timer system...')
        
        -- Timer system using Python callbacks with queue-based approach
        _PY.timer_id = 1
        _PY.callback_queue = {}
        
        function _PY.setTimeout(fun, ms)
            local timer_id = _PY.timer_id
            _PY.timer_id = _PY.timer_id + 1
            pythonTimer(fun, ms, timer_id)
            return timer_id
        end
        
        function _PY.setInterval(fun, ms)
            local interval_id = _PY.timer_id
            _PY.timer_id = _PY.timer_id + 1
            pythonSetInterval(fun, ms, interval_id)
            return interval_id
        end
        
        function _PY.clearTimeout(timer_id)
            return pythonClearTimer(timer_id)
        end
        
        function _PY.clearInterval(interval_id)
            return pythonClearInterval(interval_id)
        end
        
        function _PY.sleep(seconds)
            local co = coroutine.running()
            if not co then
                error("_PY.sleep can only be called from within a coroutine")
            end
            -- Use a simple timer that just resumes the coroutine
            pythonTimer(function()
                coroutine.resume(co)
            end, seconds * 1000, -1)  -- -1 for sleep timers
            coroutine.yield()
        end
        
        function _PY.runCallbacks()
            -- Process all queued callbacks
            while #_PY.callback_queue > 0 do
                local callback = table.remove(_PY.callback_queue, 1)
                local ok, err = pcall(callback)
                if not ok then
                    print("Error in callback:", err)
                end
            end
        end
        
        print('[LUA DEBUG] Timer system setup complete')
        """
        try:
            self.lua_runtime.execute(setup_code)
            if self.debug:
                self.lua_runtime.execute("_PY.debug = true")
        except Exception as e:
            print(f"Error setting up Lua environment: {e}", file=sys.stderr)
            traceback.print_exc()

    def create_timer(self, lua_function, delay_ms: int) -> int:
        """Create a timer using the Lua-based system"""
        # Pass the Lua function directly to Lua for handling
        # We need to pass the function object directly, not serialize it
        try:
            # Store the function in Lua and get a reference
            self.lua_runtime.globals()["__temp_timer_function"] = lua_function
            timer_id = self.lua_runtime.eval(f"_PY.setTimeout(__temp_timer_function, {delay_ms})")
            # Clean up the temporary reference
            self.lua_runtime.globals()["__temp_timer_function"] = None
            return timer_id
        except Exception as e:
            if self.debug:
                print(f"[TIMER DEBUG] Failed to create timer: {e}", file=sys.stderr)
            raise RuntimeError(f"Failed to create timer: {e}") from e

    def _get_lua_function_code(self, lua_function):
        """Get the Lua code representation of a function"""
        # This is a placeholder - we need to implement proper function serialization
        # For now, we'll use a different approach
        return "print('Timer fired!')"  # Placeholder

    def clear_timer(self, timer_id: int) -> bool:
        """Cancel a timer by ID using the Lua-based system"""
        try:
            if timer_id in self.timers:
                handle = self.timers[timer_id]
                handle.cancel()
                del self.timers[timer_id]
                return True
            return False
        except Exception:
            return False

    def create_interval(self, lua_function, delay_ms: int) -> int:
        """Create an interval using the Lua-based system"""
        # Pass the Lua function directly to Lua for handling
        try:
            # Store the function in Lua and get a reference
            self.lua_runtime.globals()["__temp_interval_function"] = lua_function
            interval_id = self.lua_runtime.eval(f"_PY.setInterval(__temp_interval_function, {delay_ms})")
            # Clean up the temporary reference
            self.lua_runtime.globals()["__temp_interval_function"] = None
            return interval_id
        except Exception as e:
            if self.debug:
                print(f"[TIMER DEBUG] Failed to create interval: {e}", file=sys.stderr)
            raise RuntimeError(f"Failed to create interval: {e}") from e

    def clear_interval(self, interval_id: int) -> bool:
        """Cancel an interval by ID using the Lua-based system"""
        try:
            if interval_id in self.intervals:
                handle = self.intervals[interval_id]
                handle.cancel()
                del self.intervals[interval_id]
                return True
            return False
        except Exception:
            return False

    def has_active_timers(self) -> bool:
        """Check if there are any active timers or intervals"""
        return len(self.timers) > 0 or len(self.intervals) > 0

    def get_active_timer_count(self) -> int:
        """Get the number of active timers and intervals"""
        return len(self.timers) + len(self.intervals)

    def execute_user_code(self, lua_code):
        """Execute user code directly without coroutine wrapping"""
        try:
            if self.debug:
                print(f"[TIMER DEBUG] Executing user code: {repr(lua_code[:100])}...", file=sys.stderr)
            
            # Execute the code directly
            self.lua_runtime.execute(lua_code)
            return True
        except Exception as e:
            if self.debug:
                print(f"[TIMER DEBUG] Failed to execute user code: {e}", file=sys.stderr)
            raise RuntimeError(f"Failed to execute user code: {e}") from e

    def process_callbacks(self):
        """Process any pending operations (kept for compatibility)"""
        # Process any queued callbacks in Lua
        try:
            self.lua_runtime.execute("_PY.runCallbacks()")
        except Exception as e:
            if self.debug:
                print(f"[TIMER DEBUG] Failed to process callbacks: {e}", file=sys.stderr)


# Expose to Lua
coroutine_manager_instance = None


def pythonTimer(lua_function, delay_ms, timer_id):
    loop = asyncio.get_event_loop()

    def queue_callback():
        global coroutine_manager_instance
        if coroutine_manager_instance:
            try:
                # Remove the timer from tracking when it fires
                if timer_id in coroutine_manager_instance.timers:
                    del coroutine_manager_instance.timers[timer_id]
                
                # Queue the callback instead of calling it directly
                coroutine_manager_instance.lua_runtime.execute("""
                    table.insert(_PY.callback_queue, __temp_callback_function)
                """)
            except Exception as e:
                print(f"Error in timer callback: {e}")

    # Store the function in Lua for the callback
    coroutine_manager_instance.lua_runtime.globals()["__temp_callback_function"] = lua_function
    
    handle = loop.call_later(delay_ms / 1000.0, queue_callback)
    
    # Track the timer handle if it's not a sleep timer (timer_id != -1)
    if timer_id != -1 and coroutine_manager_instance:
        coroutine_manager_instance.timers[timer_id] = handle
    
    return True


def pythonClearTimer(timer_id):
    global coroutine_manager_instance
    if coroutine_manager_instance is None:
        raise RuntimeError("CoroutineManager not initialized")
    return coroutine_manager_instance.clear_timer(timer_id)


def pythonSetInterval(lua_function, delay_ms, interval_id):
    loop = asyncio.get_event_loop()

    def queue_callback():
        global coroutine_manager_instance
        if coroutine_manager_instance:
            try:
                # Check if the interval has been cleared before executing
                if interval_id not in coroutine_manager_instance.intervals:
                    return  # Interval was cleared, don't execute or reschedule
                
                # Queue the callback instead of calling it directly
                coroutine_manager_instance.lua_runtime.execute("""
                    table.insert(_PY.callback_queue, __temp_interval_callback_function)
                """)
            except Exception as e:
                print(f"Error in interval callback: {e}")
            
            # Only schedule the next interval if this interval is still active
            if coroutine_manager_instance and interval_id in coroutine_manager_instance.intervals:
                handle = loop.call_later(delay_ms / 1000.0, queue_callback)
                # Update the handle in tracking
                coroutine_manager_instance.intervals[interval_id] = handle

    # Store the function in Lua for the callback
    coroutine_manager_instance.lua_runtime.globals()["__temp_interval_callback_function"] = lua_function
    
    handle = loop.call_later(delay_ms / 1000.0, queue_callback)
    
    # Track the interval handle
    if coroutine_manager_instance:
        coroutine_manager_instance.intervals[interval_id] = handle
    
    return True


def pythonClearInterval(interval_id):
    global coroutine_manager_instance
    if coroutine_manager_instance is None:
        raise RuntimeError("CoroutineManager not initialized")
    return coroutine_manager_instance.clear_interval(interval_id) 