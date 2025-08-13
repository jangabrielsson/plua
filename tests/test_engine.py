"""
Tests for the LuaEngine class.
"""

import asyncio
import pytest
from eplua import LuaEngine


class TestLuaEngine:
    """Test cases for LuaEngine."""
    
    @pytest.mark.asyncio
    async def test_engine_lifecycle(self):
        """Test engine start and stop."""
        engine = LuaEngine()
        assert not engine.is_running()
        
        await engine.start()
        assert engine.is_running()
        
        await engine.stop()
        assert not engine.is_running()
        
    @pytest.mark.asyncio
    async def test_lua_execution(self):
        """Test basic Lua code execution."""
        engine = LuaEngine()
        
        result = await engine.run_script("return 2 + 3")
        assert result == 5
        
        await engine.stop()
        
    @pytest.mark.asyncio
    async def test_lua_global_variables(self):
        """Test getting and setting Lua global variables."""
        engine = LuaEngine()
        
        # Set a global variable
        engine.set_lua_global("test_var", 42)
        
        # Get it back
        result = engine.get_lua_global("test_var")
        assert result == 42
        
        # Use it in Lua code
        result = await engine.run_script("return test_var * 2")
        assert result == 84
        
        await engine.stop()
        
    @pytest.mark.asyncio
    async def test_lua_print_function(self):
        """Test the enhanced print function."""
        engine = LuaEngine()
        
        # This should not raise an exception
        await engine.run_script('print("Hello from Lua!")')
        
        await engine.stop()
        
    @pytest.mark.asyncio
    async def test_timer_creation_from_lua(self):
        """Test creating timers from Lua code."""
        engine = LuaEngine()
        
        # Create a timeout timer
        lua_code = """
        local timer_id = timer.set_timeout(100, function()
            print("Timer fired!")
        end)
        return timer_id
        """
        
        timer_id = await engine.run_script(lua_code)
        assert timer_id is not None
        assert isinstance(timer_id, str)
        
        # Wait for timer to fire
        await asyncio.sleep(0.15)
        
        await engine.stop()
        
    @pytest.mark.asyncio
    async def test_timer_count_from_lua(self):
        """Test getting timer count from Lua."""
        engine = LuaEngine()
        
        # Initially no timers
        result = await engine.run_script("return timer.get_timer_count()")
        assert result == 0
        
        # Create a timer
        await engine.run_script("""
        timer.set_timeout(1000, function()
            print("Timer")
        end)
        """)
        
        # Should have one timer
        result = await engine.run_script("return timer.get_timer_count()")
        assert result == 1
        
        await engine.stop()
        
    @pytest.mark.asyncio
    async def test_timer_clearing_from_lua(self):
        """Test clearing timers from Lua."""
        engine = LuaEngine()
        
        lua_code = """
        local timer_id = timer.set_timeout(1000, function()
            print("This should not fire")
        end)
        
        local cleared = timer.clear_timer(timer_id)
        return cleared
        """
        
        result = await engine.run_script(lua_code)
        assert result is True
        
        await engine.stop()
        
    @pytest.mark.asyncio
    async def test_async_context_manager(self):
        """Test using engine as async context manager."""
        async with LuaEngine() as engine:
            assert engine.is_running()
            
            result = await engine.run_script("return 'context manager works'")
            assert result == "context manager works"
            
        assert not engine.is_running()
        
    @pytest.mark.asyncio
    async def test_multiple_scripts(self):
        """Test running multiple scripts with the same engine."""
        engine = LuaEngine()
        
        # Run first script
        result1 = await engine.run_script("return 10", "script1")
        assert result1 == 10
        
        # Run second script
        result2 = await engine.run_script("return 20", "script2")
        assert result2 == 20
        
        # Check loaded scripts
        scripts = engine.get_loaded_scripts()
        assert "script1" in scripts
        assert "script2" in scripts
        
        await engine.stop()
