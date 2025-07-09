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
    """Manages Lua coroutine execution with simplified Python-based callback system"""

    def __init__(self, lua_runtime: lupa.LuaRuntime, debug: bool = False):
        self.lua_runtime = lua_runtime
        self.timers = {}  # timer_id -> timer_handle
        self.intervals = {}  # interval_id -> interval_handle
        self.callback_queue = []  # Python list for queued callbacks
        self.callback_semaphore = asyncio.Semaphore(0)  # Semaphore to wake up callback loop
        self.next_id = 1
        self.main_coroutine = None  # Reference to the main coroutine
        self.lock = threading.Lock()
        self.debug = debug
        # Note: _setup_lua_environment() will be called explicitly after Python functions are exposed

    def set_main_coroutine(self, main_co):
        """Set the main coroutine that should be resumed by timers"""
        self.main_coroutine = main_co
        # Also set it in Lua
        try:
            self.lua_runtime.globals()["__main_coroutine"] = main_co
        except Exception as e:
            if self.debug:
                print(f"[TIMER DEBUG] Failed to set main coroutine in Lua: {e}", file=sys.stderr)

    def _setup_lua_environment(self):
        setup_code = """
        _PY = _PY or {}
        
        -- Timer system using Python callbacks with closure storage in Lua
        _PY.timer_id = 1
        _PY.callbacks = {}  -- Store closures in Lua for timers/intervals
        _PY.net_callbacks = {}  -- Store closures in Lua for network events
        _PY._interval_ids = {}  -- Track which callbacks are intervals
        
        function _PY.setTimeout(fun, ms)
            local timer_id = _PY.timer_id
            _PY.timer_id = _PY.timer_id + 1
            
            -- Store the closure in Lua
            _PY.callbacks[timer_id] = fun
            
            -- Pass only the timer_id to Python
            pythonTimer(timer_id, ms, timer_id)
            return timer_id
        end
        
        function _PY.setInterval(fun, ms)
            local interval_id = _PY.timer_id
            _PY.timer_id = _PY.timer_id + 1
            
            -- Store the closure in Lua
            _PY.callbacks[interval_id] = fun
            -- Mark this as an interval
            _PY._interval_ids[interval_id] = true
            
            -- Pass only the interval_id to Python
            pythonSetInterval(interval_id, ms, interval_id)
            return interval_id
        end
        
        function _PY.clearTimeout(timer_id)
            -- Remove the callback from Lua storage
            _PY.callbacks[timer_id] = nil
            return pythonClearTimer(timer_id)
        end
        
        function _PY.clearInterval(interval_id)
            -- Remove the callback from Lua storage
            _PY.callbacks[interval_id] = nil
            -- Remove from interval tracking
            _PY._interval_ids[interval_id] = nil
            return pythonClearInterval(interval_id)
        end
        
        function _PY.sleep(seconds)
            -- Use a blocking sleep that doesn't require coroutines
            -- This is simpler and works in all contexts
            local start_time = os.time()
            while os.time() - start_time < seconds do
                -- Small delay to avoid busy waiting
                os.execute("sleep 0.1")
            end
        end
        
        -- Function to execute a callback by ID (called from Python)
        function _PY.executeCallback(callback_id)
            local callback = _PY.callbacks[callback_id]
            if callback then
                -- Always wrap callback in a coroutine for consistency
                local co = coroutine.create(callback)
                local success, result = coroutine.resume(co)
                if not success then
                    print("[ERROR] Timer callback failed:", result)
                else
                    -- Check if coroutine is dead (finished) or suspended (waiting)
                    local status = coroutine.status(co)
                    if status == "dead" then
                        -- Coroutine finished normally, remove callback
                        if callback_id > 0 and not _PY._interval_ids[callback_id] then
                            _PY.callbacks[callback_id] = nil
                        end
                    elseif status == "suspended" then
                        -- Coroutine yielded, keep it for future resumption
                        -- Store the coroutine for potential future resume
                        _PY.callbacks[callback_id] = co
                    end
                end
            end
        end
        
        -- Function to execute a network callback by ID with parameters (called from Python)
        function _PY.executeCallbackWithParams(callback_id, ...)
            if _PY.debug then
                print("[DEBUG] executeCallbackWithParams: called with ID", callback_id, "and args:", ...)
            end
            local callback = _PY.net_callbacks[callback_id]
            if callback then
                if _PY.debug then
                    print("[DEBUG] executeCallbackWithParams: executing callback")
                end
                -- Always wrap callback in a coroutine for consistency
                local args = {...}
                local co = coroutine.create(function()
                    return callback(table.unpack(args))
                end)
                local success, result = coroutine.resume(co)
                if not success then
                    print("[ERROR] Network callback failed:", result)
                else
                    if _PY.debug then
                        print("[DEBUG] executeCallbackWithParams: callback executed successfully, result:", result)
                        -- Check if coroutine is dead (finished) or suspended (waiting)
                        local status = coroutine.status(co)
                        print("[DEBUG] executeCallbackWithParams: coroutine status:", status)
                        if status == "dead" then
                            -- Coroutine finished normally, remove callback
                            _PY.net_callbacks[callback_id] = nil
                            print("[DEBUG] executeCallbackWithParams: callback removed (dead)")
                        elseif status == "suspended" then
                            -- Coroutine yielded, keep it for future resumption
                            _PY.net_callbacks[callback_id] = co
                            print("[DEBUG] executeCallbackWithParams: callback kept for resumption (suspended)")
                        end
                    else
                        -- Check if coroutine is dead (finished) or suspended (waiting)
                        local status = coroutine.status(co)
                        if status == "dead" then
                            -- Coroutine finished normally, remove callback
                            _PY.net_callbacks[callback_id] = nil
                        elseif status == "suspended" then
                            -- Coroutine yielded, keep it for future resumption
                            _PY.net_callbacks[callback_id] = co
                        end
                    end
                end
            else
                if _PY.debug then
                    print("[DEBUG] executeCallbackWithParams: no callback found for ID", callback_id)
                end
            end
        end
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

    def _lua_escape_string(self, s):
        """Escape a string for safe use as a Lua string literal (double-quoted)."""
        if not isinstance(s, str):
            s = str(s)
        
        # Handle Unicode and special characters properly
        result = []
        for char in s:
            if char == '\\':
                result.append(r'\\')
            elif char == '"':
                result.append(r'\"')
            elif char == '\n':
                result.append(r'\n')
            elif char == '\r':
                result.append(r'\r')
            elif char == '\t':
                result.append(r'\t')
            elif char == '\b':
                result.append(r'\b')
            elif char == '\f':
                result.append(r'\f')
            elif ord(char) < 32 or ord(char) > 126:
                # Escape non-printable and non-ASCII characters using Lua's escape sequences
                if ord(char) < 256:
                    result.append(f'\\{ord(char):03d}')
                else:
                    # For Unicode characters, use UTF-8 encoding
                    result.append(char)
            else:
                result.append(char)
        
        return ''.join(result)

    def process_callbacks(self):
        """Process all queued callbacks in Lua context"""
        # print(f"[DEBUG] process_callbacks: called, queue size: {len(self.callback_queue)}")
        with self.lock:
            if not self.callback_queue:
                # print("[DEBUG] process_callbacks: no callbacks to process")
                return
            callbacks_to_process = self.callback_queue.copy()
            self.callback_queue.clear()
            # print(f"[DEBUG] process_callbacks: processing {len(callbacks_to_process)} callbacks")
        for i, callback_data in enumerate(callbacks_to_process):
            try:
                # print(f"[DEBUG] process_callbacks: processing callback {i+1}/{len(callbacks_to_process)}: {callback_data}")
                if isinstance(callback_data, tuple):
                    callback_id = callback_data[0]
                    args = callback_data[1:]
                    # print(f"[DEBUG] process_callbacks: callback with params - ID: {callback_id}, args: {args}")
                    lua_args = []
                    for arg in args:
                        if arg is True:
                            lua_args.append("true")
                        elif arg is False:
                            lua_args.append("false")
                        elif arg is None:
                            lua_args.append("nil")
                        elif isinstance(arg, str):
                            # Use improved Lua string escaping
                            escaped = self._lua_escape_string(arg)
                            lua_args.append(f'"{escaped}"')
                        else:
                            lua_args.append(str(arg))
                    args_str = ", ".join(lua_args)
                    if args_str:
                        call = f"_PY.executeCallbackWithParams({callback_id}, {args_str})"
                    else:
                        call = f"_PY.executeCallbackWithParams({callback_id})"
                    if self.debug:
                        print(f"[DEBUG] process_callbacks: executing {call}")
                    try:
                        self.lua_runtime.execute(call)
                    except Exception as e:
                        print(f"[DEBUG] Failed to execute: {call}")
                        print(f"[DEBUG] Error: {e}")
                        raise
                else:
                    callback_id = callback_data
                    # print(f"[DEBUG] process_callbacks: executing _PY.executeCallback({callback_id})")
                    self.lua_runtime.execute(f"_PY.executeCallback({callback_id})")
                # print(f"[DEBUG] process_callbacks: callback {i+1} executed successfully")
            except Exception as e:
                print(f"[PY ERROR] Exception executing callback ID {callback_id}: {e}")
                import traceback
                traceback.print_exc()
        # print("[DEBUG] process_callbacks: finished processing all callbacks")


# Expose to Lua
coroutine_manager_instance = None


def queue_callback_with_params(callback_id, *args):
    """Queue a callback with parameters for execution in Lua context"""
    global coroutine_manager_instance
    if coroutine_manager_instance:
        try:
            # Queue the callback ID and parameters for execution in Lua
            with coroutine_manager_instance.lock:
                coroutine_manager_instance.callback_queue.append((callback_id, *args))
            
            # Wake up the callback loop
            coroutine_manager_instance.callback_semaphore.release()
        except Exception as e:
            print(f"Error in callback with params: {e}")
            import traceback
            traceback.print_exc()


def pythonTimer(callback_id, delay_ms, timer_id):
    def queue_callback():
        global coroutine_manager_instance
        if coroutine_manager_instance:
            try:
                # Remove the timer from tracking when it fires
                if timer_id in coroutine_manager_instance.timers:
                    del coroutine_manager_instance.timers[timer_id]
                
                # Queue the callback ID for execution in Lua
                with coroutine_manager_instance.lock:
                    coroutine_manager_instance.callback_queue.append(callback_id)
                
                # Wake up the callback loop
                coroutine_manager_instance.callback_semaphore.release()
            except Exception as e:
                print(f"Error in timer callback: {e}")
                import traceback
                traceback.print_exc()

    # Use asyncio.create_task with asyncio.sleep instead of loop.call_later
    # This ensures the callback is queued properly and doesn't execute immediately
    async def delayed_callback():
        await asyncio.sleep(delay_ms / 1000.0)
        queue_callback()

    handle = asyncio.create_task(delayed_callback())
    
    # Track the timer handle if it's not a sleep timer (timer_id != -1)
    if timer_id != -1 and coroutine_manager_instance:
        coroutine_manager_instance.timers[timer_id] = handle
    
    return True


def pythonClearTimer(timer_id):
    global coroutine_manager_instance
    if coroutine_manager_instance is None:
        raise RuntimeError("CoroutineManager not initialized")
    return coroutine_manager_instance.clear_timer(timer_id)


def pythonSetInterval(callback_id, delay_ms, interval_id):

    def queue_callback():
        global coroutine_manager_instance
        if coroutine_manager_instance:
            try:
                # Check if the interval has been cleared before executing
                if interval_id not in coroutine_manager_instance.intervals:
                    return  # Interval was cleared, don't execute or reschedule
                
                # Queue the callback ID for execution in Lua
                with coroutine_manager_instance.lock:
                    coroutine_manager_instance.callback_queue.append(callback_id)
                
                # Wake up the callback loop
                coroutine_manager_instance.callback_semaphore.release()
            except Exception as e:
                print(f"Error in interval callback: {e}")
            
            # Only schedule the next interval if this interval is still active
            if coroutine_manager_instance and interval_id in coroutine_manager_instance.intervals:
                # Schedule the next interval using asyncio.create_task
                async def next_interval():
                    await asyncio.sleep(delay_ms / 1000.0)
                    queue_callback()
                
                handle = asyncio.create_task(next_interval())
                # Update the handle in tracking
                coroutine_manager_instance.intervals[interval_id] = handle

    # Use asyncio.create_task with asyncio.sleep instead of loop.call_later
    # This ensures the callback is queued properly and doesn't execute immediately
    async def delayed_callback():
        await asyncio.sleep(delay_ms / 1000.0)
        queue_callback()

    handle = asyncio.create_task(delayed_callback())
    
    # Track the interval handle
    if coroutine_manager_instance:
        coroutine_manager_instance.intervals[interval_id] = handle
    
    return True


def pythonClearInterval(interval_id):
    global coroutine_manager_instance
    if coroutine_manager_instance is None:
        raise RuntimeError("CoroutineManager not initialized")
    return coroutine_manager_instance.clear_interval(interval_id) 