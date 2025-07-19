"""
Tests for the unified callback system
"""

import pytest
import asyncio
from plua2.runtime import LuaAsyncRuntime


class TestCallbackSystem:
    """Test cases for the unified callback system"""
    
    @pytest.mark.asyncio
    async def test_timer_callback_integration(self):
        """Test that timers use the unified callback system"""
        runtime = LuaAsyncRuntime()
        runtime.initialize_lua()

        # Create a timer using Lua setTimeout
        script = """
        executed = false  -- Global variable
        setTimeout(function()
            executed = true
        end, 100)
        return executed
        """

        # Execute script and verify timer was created but not executed yet
        result = runtime.interpreter.lua.execute(script)
        assert result == False  # Timer hasn't executed yet

        # Wait for timer to execute
        await asyncio.sleep(0.2)

        # Check that the timer executed
        result = runtime.interpreter.lua.eval("executed")
        assert result == True
    
    @pytest.mark.asyncio
    async def test_manual_callback_registration(self):
        """Test manual callback registration and execution"""
        runtime = LuaAsyncRuntime()
        runtime.initialize_lua()
        
        # Register a callback manually
        script = """
        result = nil  -- Global variable
        callback_id = _PY.registerCallback(function(data)
            result = data
        end, false)
        return callback_id
        """
        
        callback_id = runtime.interpreter.lua.execute(script)
        assert callback_id is not None
        
        # Execute the callback with data
        runtime.interpreter.execute_lua_callback(callback_id, "test_data")
        
        # Verify the callback received the data
        result = runtime.interpreter.lua.eval("result")
        assert result == "test_data"
    
    @pytest.mark.asyncio
    async def test_persistent_vs_nonpersistent_callbacks(self):
        """Test that persistent callbacks aren't cleaned up after execution"""
        runtime = LuaAsyncRuntime()
        runtime.initialize_lua()
         # Register both types of callbacks
        script = """
        persistent_calls = 0  -- Global variables
        nonpersistent_calls = 0

        persistent_id = _PY.registerCallback(function()
            persistent_calls = persistent_calls + 1
        end, true)

        nonpersistent_id = _PY.registerCallback(function()
            nonpersistent_calls = nonpersistent_calls + 1
        end, false)

        return persistent_id, nonpersistent_id
        """
        
        persistent_id, nonpersistent_id = runtime.interpreter.lua.execute(script)
        
        # Execute each callback once
        runtime.interpreter.execute_lua_callback(persistent_id, None)
        runtime.interpreter.execute_lua_callback(nonpersistent_id, None)
        
        # Execute persistent callback again (should work)
        runtime.interpreter.execute_lua_callback(persistent_id, None)
        
        # Try to execute non-persistent callback again (should not increment)
        runtime.interpreter.execute_lua_callback(nonpersistent_id, None)
        
        # Check results
        persistent_calls = runtime.interpreter.lua.eval("persistent_calls")
        nonpersistent_calls = runtime.interpreter.lua.eval("nonpersistent_calls")
        
        assert persistent_calls == 2  # Called twice
        assert nonpersistent_calls == 1  # Only called once (cleaned up after first call)
    
    @pytest.mark.asyncio
    async def test_timer_cancellation_with_unified_system(self):
        """Test that timer cancellation works with the unified callback system"""
        runtime = LuaAsyncRuntime()
        runtime.initialize_lua()
        
        # Create and cancel a timer
        script = """
        executed = false  -- Global variable
        timer_id = setTimeout(function()
            executed = true
        end, 200)

        -- Cancel the timer after 50ms
        setTimeout(function()
            clearTimeout(timer_id)
        end, 50)

        return timer_id
        """
        
        timer_id = runtime.interpreter.lua.execute(script)
        assert timer_id is not None
        
        # Wait longer than the original timer delay
        await asyncio.sleep(0.3)
        
        # Verify the timer was cancelled and didn't execute
        executed = runtime.interpreter.lua.eval("executed")
        assert executed == False
    
    @pytest.mark.asyncio
    async def test_callback_error_handling(self):
        """Test that callback errors are handled gracefully"""
        runtime = LuaAsyncRuntime()
        runtime.initialize_lua()
        
        # Register a callback that will throw an error
        script = """
        local callback_id = _PY.registerCallback(function()
            error("Test error in callback")
        end, false)
        return callback_id
        """
        
        callback_id = runtime.interpreter.lua.execute(script)
        
        # Executing the callback should not crash the system
        # The error should be caught and handled gracefully
        try:
            runtime.interpreter.execute_lua_callback(callback_id, None)
        except Exception:
            # Some error handling is expected
            pass
        
        # Verify the system is still functional
        result = runtime.interpreter.lua.eval("2 + 2")
        assert result == 4
