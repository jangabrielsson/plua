"""
Tests for the _PY.config table functionality
"""

import pytest
import os
from plua2.runtime import LuaAsyncRuntime


class TestPyConfig:
    """Test cases for _PY.config table"""
    
    @pytest.mark.asyncio
    async def test_config_table_exists(self):
        """Test that _PY.config table exists and has basic fields"""
        runtime = LuaAsyncRuntime()
        runtime.initialize_lua()
        
        script = """
        config_type = type(_PY.config)
        has_homedir = _PY.config.homedir ~= nil
        has_platform = _PY.config.platform ~= nil
        has_debug = type(_PY.config.debug) == "boolean"
        has_fileseparator = _PY.config.fileseparator ~= nil
        """
        
        runtime.interpreter.lua.execute(script)
        
        config_type = runtime.interpreter.lua.eval("config_type")
        has_homedir = runtime.interpreter.lua.eval("has_homedir")
        has_platform = runtime.interpreter.lua.eval("has_platform")
        has_debug = runtime.interpreter.lua.eval("has_debug")
        has_fileseparator = runtime.interpreter.lua.eval("has_fileseparator")
        
        assert config_type == "table"
        assert has_homedir == True
        assert has_platform == True
        assert has_debug == True
        assert has_fileseparator == True
    
    @pytest.mark.asyncio
    async def test_config_platform_detection(self):
        """Test that platform is correctly detected"""
        runtime = LuaAsyncRuntime()
        runtime.initialize_lua()
        
        script = """
        platform = _PY.config.platform
        """
        
        runtime.interpreter.lua.execute(script)
        platform = runtime.interpreter.lua.eval("platform")
        
        # Should be one of the expected platforms
        assert platform in ["windows", "linux", "darwin"]
    
    @pytest.mark.asyncio
    async def test_config_paths(self):
        """Test that path configurations are valid"""
        runtime = LuaAsyncRuntime()
        runtime.initialize_lua()
        
        script = """
        homedir = _PY.config.homedir
        cwd = _PY.config.cwd
        filesep = _PY.config.fileseparator
        pathsep = _PY.config.pathseparator
        """
        
        runtime.interpreter.lua.execute(script)
        
        homedir = runtime.interpreter.lua.eval("homedir")
        cwd = runtime.interpreter.lua.eval("cwd")
        filesep = runtime.interpreter.lua.eval("filesep")
        pathsep = runtime.interpreter.lua.eval("pathsep")
        
        # Basic validation
        assert isinstance(homedir, str) and len(homedir) > 0
        assert isinstance(cwd, str) and len(cwd) > 0
        assert filesep in ["/", "\\"]
        assert pathsep in [":", ";"]
        
        # cwd should be accessible
        assert os.path.exists(cwd)
    
    @pytest.mark.asyncio
    async def test_config_version_info(self):
        """Test that version information is present"""
        runtime = LuaAsyncRuntime()
        runtime.initialize_lua()
        
        script = """
        plua2_version = _PY.config.plua2_version
        lua_version = _PY.config.lua_version
        python_version = _PY.config.python_version
        """
        
        runtime.interpreter.lua.execute(script)
        
        plua2_version = runtime.interpreter.lua.eval("plua2_version")
        lua_version = runtime.interpreter.lua.eval("lua_version")
        python_version = runtime.interpreter.lua.eval("python_version")
        
        assert isinstance(plua2_version, str) and len(plua2_version) > 0
        assert isinstance(lua_version, str) and len(lua_version) > 0
        assert isinstance(python_version, str) and len(python_version) > 0
        
        # Basic format validation
        assert "." in python_version  # Should have major.minor format
        assert lua_version.startswith("5.")  # Should be Lua 5.x
