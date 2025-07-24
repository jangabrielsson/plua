"""
Tests for the getenv_with_dotenv function
"""

import pytest
import os
import tempfile
from plua.runtime import LuaAsyncRuntime


class TestGetenvWithDotenv:
    """Test cases for .env file environment variable loading"""
    
    @pytest.mark.asyncio
    async def test_getenv_dotenv_basic(self):
        """Test basic .env file loading"""
        runtime = LuaAsyncRuntime()
        runtime.initialize_lua()
        
        # Create a temporary .env file
        env_content = """
DATABASE_URL=postgresql://localhost:5432/test
API_KEY="test-key-123"
DEBUG=true
"""
        
        # Save current directory and create temp .env
        original_cwd = os.getcwd()
        
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                os.chdir(temp_dir)
                
                with open('.env', 'w') as f:
                    f.write(env_content)
                
                script = """
                db_url = _PY.getenv_dotenv("DATABASE_URL", "not found")
                api_key = _PY.getenv_dotenv("API_KEY", "not found")
                debug = _PY.getenv_dotenv("DEBUG", "false")
                nonexistent = _PY.getenv_dotenv("NONEXISTENT", "default")
                """
                
                runtime.interpreter.lua.execute(script)
                
                # Check results
                db_url = runtime.interpreter.lua.eval("db_url")
                api_key = runtime.interpreter.lua.eval("api_key")
                debug = runtime.interpreter.lua.eval("debug")
                nonexistent = runtime.interpreter.lua.eval("nonexistent")
                
                assert db_url == "postgresql://localhost:5432/test"
                assert api_key == "test-key-123"
                assert debug == "true"
                assert nonexistent == "default"
                
        finally:
            os.chdir(original_cwd)
    
    @pytest.mark.asyncio
    async def test_getenv_dotenv_fallback_to_system(self):
        """Test fallback to system environment variables"""
        runtime = LuaAsyncRuntime()
        runtime.initialize_lua()
        
        # Set a system environment variable
        os.environ['TEST_SYSTEM_VAR'] = 'system_value'
        
        # Save current directory 
        original_cwd = os.getcwd()
        
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                os.chdir(temp_dir)
                
                # No .env file, should fall back to system env
                script = """
                system_var = _PY.getenv_dotenv("TEST_SYSTEM_VAR", "not found")
                """
                
                runtime.interpreter.lua.execute(script)
                system_var = runtime.interpreter.lua.eval("system_var")
                
                assert system_var == "system_value"
                
        finally:
            # Clean up
            if 'TEST_SYSTEM_VAR' in os.environ:
                del os.environ['TEST_SYSTEM_VAR']
            os.chdir(original_cwd)
    
    @pytest.mark.asyncio 
    async def test_getenv_dotenv_precedence(self):
        """Test that .env file takes precedence over system env"""
        runtime = LuaAsyncRuntime()
        runtime.initialize_lua()
        
        # Set a system environment variable
        os.environ['TEST_PRECEDENCE_VAR'] = 'system_value'
        
        env_content = """
TEST_PRECEDENCE_VAR=dotenv_value
"""
        
        # Save current directory
        original_cwd = os.getcwd()
        
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                os.chdir(temp_dir)
                
                with open('.env', 'w') as f:
                    f.write(env_content)
                
                script = """
                precedence_var = _PY.getenv_dotenv("TEST_PRECEDENCE_VAR", "not found")
                """
                
                runtime.interpreter.lua.execute(script)
                precedence_var = runtime.interpreter.lua.eval("precedence_var")
                
                # .env file should take precedence
                assert precedence_var == "dotenv_value"
                
        finally:
            # Clean up
            if 'TEST_PRECEDENCE_VAR' in os.environ:
                del os.environ['TEST_PRECEDENCE_VAR']
            os.chdir(original_cwd)
