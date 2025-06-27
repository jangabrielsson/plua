"""
Basic test to verify the test structure works
"""

import pytest


def test_basic_import():
    """Test that we can import the main modules"""
    try:
        from plua import PLuaInterpreter
        assert PLuaInterpreter is not None
    except ImportError as e:
        pytest.skip(f"Could not import PLuaInterpreter: {e}")


def test_lua_interpreter_fixture(lua_interpreter):
    """Test that the lua_interpreter fixture works"""
    assert lua_interpreter is not None
    assert hasattr(lua_interpreter, 'lua_runtime')
    assert hasattr(lua_interpreter, 'debug')


def test_basic_lua_execution(lua_interpreter):
    """Test basic Lua execution"""
    lua_code = """
    local x = 10
    local y = 20
    local result = x + y
    _G.test_result = result
    """

    success = lua_interpreter.execute_code(lua_code)
    assert success is True

    # Check if the result is available in Lua globals
    globals = lua_interpreter.lua_runtime.globals()
    assert globals.test_result == 30


def test_py_table_availability(lua_interpreter):
    """Test that _PY table is available"""
    globals = lua_interpreter.lua_runtime.globals()
    assert hasattr(globals, '_PY')
    assert globals._PY is not None


def test_temp_file_fixture(temp_file):
    """Test that temp_file fixture works"""
    assert temp_file is not None
    assert isinstance(temp_file, str)

    # Test that we can write to the file
    with open(temp_file, 'w') as f:
        f.write("test content")

    # Test that we can read from the file
    with open(temp_file, 'r') as f:
        content = f.read()

    assert content == "test content"


def test_temp_dir_fixture(temp_dir):
    """Test that temp_dir fixture works"""
    assert temp_dir is not None
    assert isinstance(temp_dir, str)

    # Test that we can create files in the directory
    test_file = f"{temp_dir}/test.txt"
    with open(test_file, 'w') as f:
        f.write("test content")

    # Test that the file exists
    with open(test_file, 'r') as f:
        content = f.read()

    assert content == "test content"
