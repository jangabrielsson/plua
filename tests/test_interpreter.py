"""
Tests for the LuaInterpreter class
"""

import pytest
from plua2.interpreter import LuaInterpreter


class TestLuaInterpreter:
    """Test cases for LuaInterpreter"""
    
    def test_initialization(self):
        """Test that interpreter can be created"""
        interpreter = LuaInterpreter()
        assert not interpreter.is_initialized()
    
    def test_initialize_with_functions(self):
        """Test initialization with Python functions"""
        interpreter = LuaInterpreter()
        
        # Mock functions
        def mock_timer(timer_id: int, delay_ms: int):
            return f"timer_{timer_id}_{delay_ms}"
        
        def mock_cancel(timer_id: int) -> bool:
            return True
        
        interpreter.initialize(mock_timer, mock_cancel)
        assert interpreter.is_initialized()
    
    def test_execute_simple_script(self):
        """Test executing a simple Lua script"""
        interpreter = LuaInterpreter()
        
        def mock_timer(timer_id: int, delay_ms: int):
            pass
        
        def mock_cancel(timer_id: int) -> bool:
            return True
        
        interpreter.initialize(mock_timer, mock_cancel)
        
        # Simple script that doesn't use timers
        script = 'local x = 5 + 3; print("Result:", x)'
        interpreter.execute_script(script)
    
    def test_execute_without_initialization(self):
        """Test that executing without initialization raises error"""
        interpreter = LuaInterpreter()
        
        with pytest.raises(RuntimeError):
            interpreter.execute_script("print('test')")
    
    def test_execute_callback_without_initialization(self):
        """Test that executing callback without initialization raises error"""
        interpreter = LuaInterpreter()
        
        with pytest.raises(RuntimeError):
            interpreter.execute_lua_callback(1, None)
