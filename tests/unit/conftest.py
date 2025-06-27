"""
Pytest configuration and common fixtures for PLua tests
"""

import pytest
import tempfile
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def lua_interpreter():
    """Create a fresh Lua interpreter instance for each test"""
    from plua import PLuaInterpreter
    return PLuaInterpreter(debug=False)


@pytest.fixture
def debug_lua_interpreter():
    """Create a fresh Lua interpreter instance with debug enabled"""
    from plua import PLuaInterpreter
    return PLuaInterpreter(debug=True)


@pytest.fixture
def temp_file():
    """Create a temporary file that gets cleaned up after the test"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.lua') as f:
        yield f.name
    # Clean up
    try:
        os.unlink(f.name)
    except OSError:
        pass


@pytest.fixture
def temp_dir():
    """Create a temporary directory that gets cleaned up after the test"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def sample_lua_file(temp_file):
    """Create a sample Lua file for testing"""
    content = """
-- Sample Lua file for testing
local x = 10
local y = 20
local result = x + y
print("Result:", result)
return result
"""
    with open(temp_file, 'w') as f:
        f.write(content)
    return temp_file


@pytest.fixture
def error_lua_file(temp_file):
    """Create a Lua file with syntax errors for testing"""
    content = """
-- Lua file with syntax error
local x = 10
local y = 20
local result = x + y
print("Result:", result)
-- Missing closing brace
if x > 5 then
    print("x is greater than 5"
"""
    with open(temp_file, 'w') as f:
        f.write(content)
    return temp_file
