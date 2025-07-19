"""
Tests for file operations and main_file_hook functionality
"""

import pytest
import tempfile
import os
from plua2.interpreter import LuaInterpreter


class TestFileOperations:
    """Test cases for file loading and main_file_hook"""
    
    def test_main_file_hook_default(self):
        """Test default main_file_hook implementation"""
        interpreter = LuaInterpreter()
        
        # Mock functions for initialization
        def mock_timer(timer_id: int, delay_ms: int):
            return f"timer_{timer_id}_{delay_ms}"
        
        def mock_cancel(timer_id: int) -> bool:
            return True
        
        interpreter.initialize(mock_timer, mock_cancel)
        
        # Create a temporary Lua file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.lua', delete=False) as f:
            f.write('test_variable = "file_loaded"')
            temp_file = f.name
        
        try:
            # Execute file using main_file_hook
            interpreter.execute_file(temp_file)
            
            # Verify the file was loaded
            result = interpreter.lua.eval('test_variable')
            assert result == "file_loaded"
            
        finally:
            os.unlink(temp_file)
    
    def test_main_file_hook_override(self):
        """Test overriding main_file_hook"""
        interpreter = LuaInterpreter()
        
        def mock_timer(timer_id: int, delay_ms: int):
            return f"timer_{timer_id}_{delay_ms}"
        
        def mock_cancel(timer_id: int) -> bool:
            return True
        
        interpreter.initialize(mock_timer, mock_cancel)
        
        # Override the main_file_hook
        override_script = """
        function _PY.main_file_hook(filename)
            print("Custom hook processing: " .. filename)
            -- Set a variable to indicate custom hook was called
            custom_hook_called = true
            
            -- Still load the file, but with custom processing
            local file = io.open(filename, "r")
            if file then
                local content = file:read("*all")
                file:close()
                
                -- Add custom preprocessing - convert all variables to uppercase
                content = content:gsub("test_variable", "TEST_VARIABLE")
                
                local func, err = load(content, "@" .. filename)
                if func then
                    coroutine.wrap(func)()
                else
                    error("Failed to load: " .. tostring(err))
                end
            end
        end
        """
        
        interpreter.execute_script(override_script)
        
        # Create a test file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.lua', delete=False) as f:
            f.write('test_variable = "processed_by_custom_hook"')
            temp_file = f.name
        
        try:
            # Execute file - should use custom hook
            interpreter.execute_file(temp_file)
            
            # Verify custom hook was called
            custom_hook_called = interpreter.lua.eval('custom_hook_called')
            assert custom_hook_called == True
            
            # Verify the custom processing occurred
            result = interpreter.lua.eval('TEST_VARIABLE')  # Should be uppercase
            assert result == "processed_by_custom_hook"
            
        finally:
            os.unlink(temp_file)
    
    def test_file_not_found_error(self):
        """Test error handling when file doesn't exist"""
        interpreter = LuaInterpreter()
        
        def mock_timer(timer_id: int, delay_ms: int):
            return f"timer_{timer_id}_{delay_ms}"
        
        def mock_cancel(timer_id: int) -> bool:
            return True
        
        interpreter.initialize(mock_timer, mock_cancel)
        
        # Try to load non-existent file
        with pytest.raises(RuntimeError) as excinfo:
            interpreter.execute_file("/nonexistent/file.lua")
        
        assert "main_file_hook failed" in str(excinfo.value)
    
    def test_file_syntax_error_handling(self):
        """Test handling of syntax errors in loaded files"""
        interpreter = LuaInterpreter()
        
        def mock_timer(timer_id: int, delay_ms: int):
            return f"timer_{timer_id}_{delay_ms}"
        
        def mock_cancel(timer_id: int) -> bool:
            return True
        
        interpreter.initialize(mock_timer, mock_cancel)
        
        # Create a file with syntax error
        with tempfile.NamedTemporaryFile(mode='w', suffix='.lua', delete=False) as f:
            f.write('invalid lua syntax !@#$%')
            temp_file = f.name
        
        try:
            # Should raise error due to syntax error
            with pytest.raises(RuntimeError) as excinfo:
                interpreter.execute_file(temp_file)
            
            assert "main_file_hook failed" in str(excinfo.value)
            
        finally:
            os.unlink(temp_file)
    
    def test_fibaro_hook_integration(self):
        """Test that Fibaro module overrides main_file_hook correctly"""
        interpreter = LuaInterpreter()
        
        def mock_timer(timer_id: int, delay_ms: int):
            return f"timer_{timer_id}_{delay_ms}"
        
        def mock_cancel(timer_id: int) -> bool:
            return True
        
        interpreter.initialize(mock_timer, mock_cancel)
        
        # Load Fibaro module (which should override main_file_hook)
        interpreter.execute_script("require('fibaro')")
        
        # Create a test file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.lua', delete=False) as f:
            f.write('fibaro_test_var = "fibaro_processed"')
            temp_file = f.name
        
        try:
            # Execute file - should use Fibaro's hook
            interpreter.execute_file(temp_file)
            
            # Verify the file was processed
            result = interpreter.lua.eval('fibaro_test_var')
            assert result == "fibaro_processed"
            
            # Verify Fibaro globals are available
            fibaro_available = interpreter.lua.eval('fibaro ~= nil')
            api_available = interpreter.lua.eval('api ~= nil')
            
            assert fibaro_available == True
            assert api_available == True
            
        finally:
            os.unlink(temp_file)
