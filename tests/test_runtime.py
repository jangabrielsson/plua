"""
Tests for the LuaAsyncRuntime class
"""

import pytest
import asyncio
from plua.runtime import LuaAsyncRuntime


class TestLuaAsyncRuntime:
    """Test cases for LuaAsyncRuntime"""
    
    def test_initialization(self):
        """Test that runtime can be created"""
        runtime = LuaAsyncRuntime()
        assert runtime.interpreter is not None
        assert not runtime.interpreter.is_initialized()
    
    @pytest.mark.asyncio
    async def test_simple_timer_creation(self):
        """Test creating a simple timer"""
        runtime = LuaAsyncRuntime()
        runtime.initialize_lua()
        
        # Create a timer
        task = runtime.create_timer(1, 100)
        assert task is not None
        assert 1 in runtime.timer_tasks
        
        # Cancel the timer to clean up
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
    
    @pytest.mark.asyncio
    async def test_timer_cancellation(self):
        """Test timer cancellation"""
        runtime = LuaAsyncRuntime()
        runtime.initialize_lua()
        
        # Create a timer
        task = runtime.create_timer(1, 1000)
        assert 1 in runtime.timer_tasks
        
        # Cancel it
        success = runtime.python_cancel_timer(1)
        assert success
        assert 1 not in runtime.timer_tasks
        
        # Try to cancel again
        success = runtime.python_cancel_timer(1)
        assert not success
    
    @pytest.mark.asyncio
    async def test_short_duration_run(self):
        """Test running for a short duration"""
        runtime = LuaAsyncRuntime()
        
        script = """
        print("Test script running")
        setTimeout(function() print("Timer fired") end, 50)
        """
        
        # Run for 1 second
        await runtime.start(main_script=script, duration=1)
