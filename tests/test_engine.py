"""
Tests for the LuaEngine class.
"""

import asyncio
import pytest
from plua import LuaEngine


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
        await engine.start()
        
        result = await engine.run_script("return 2 + 3")
        assert result == 5
        
        await engine.stop()
        
    @pytest.mark.asyncio
    async def test_lua_global_variables(self):
        """Test getting and setting Lua global variables."""
        engine = LuaEngine()
        await engine.start()
        
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
        await engine.start()
        
        # This should not raise an exception
        await engine.run_script('print("Hello from Lua!")')
        
        await engine.stop()
        
    @pytest.mark.asyncio
    async def test_timer_creation_from_lua(self):
        """Test creating timers from Lua code."""
        engine = LuaEngine()
        await engine.start()
        
        # Create a timeout timer using global setTimeout
        lua_code = """
        local timer_id = setTimeout(function()
            print("Timer fired!")
        end, 100)
        return timer_id
        """
        
        timer_id = await engine.run_script(lua_code)
        assert timer_id is not None
        assert isinstance(timer_id, int)  # Lua callback ID is an integer
        
        # Wait for timer to fire
        await asyncio.sleep(0.15)
        
        await engine.stop()
        
    @pytest.mark.asyncio
    async def test_timer_count_from_lua(self):
        """Test getting timer count from Lua."""
        engine = LuaEngine()
        await engine.start()
        
        # Initially no timers
        result = await engine.run_script("return _PY.get_timer_count()")
        assert result == 0
        
        # Create a timer
        await engine.run_script("""
        setTimeout(function()
            print("Timer")
        end, 1000)
        """)
        
        # Should have one timer
        result = await engine.run_script("return _PY.get_timer_count()")
        assert result == 1
        
        await engine.stop()
        
    @pytest.mark.asyncio
    async def test_timer_clearing_from_lua(self):
        """Test clearing timers from Lua."""
        engine = LuaEngine()
        await engine.start()
        
        lua_code = """
        local timer_id = setTimeout(function()
            print("This should not fire")
        end, 1000)
        
        clearTimeout(timer_id)
        return true  -- Just return success since clearTimeout doesn't return value
        """
        
        result = await engine.run_script(lua_code)
        assert result is True
        
        await engine.stop()
        
    @pytest.mark.asyncio
    async def test_interval_from_lua(self):
        """Test setInterval functionality from Lua."""
        engine = LuaEngine()
        await engine.start()
        
        # Test setInterval (implemented in Lua using setTimeout)
        lua_code = """
        local count = 0
        local interval_id = setInterval(function()
            count = count + 1
            _G.test_count = count
            if count >= 3 then
                clearInterval(interval_id)
            end
        end, 50)
        return interval_id
        """
        
        interval_id = await engine.run_script(lua_code)
        assert interval_id is not None
        assert isinstance(interval_id, int)
        
        # Wait for interval to run a few times
        await asyncio.sleep(0.2)
        
        # Check that the count was incremented
        count = engine.get_lua_global("test_count")
        assert count == 3
        
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
        await engine.start()
        
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
