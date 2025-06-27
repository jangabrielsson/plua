"""
Tests for core extensions (timers, I/O, system functions)
"""

import time
from unittest.mock import patch


def create_lua_result_table(lua_interpreter):
    """Helper function to create a Lua table for storing test results"""
    lua_interpreter.lua_runtime.globals()['result'] = None
    return lua_interpreter.lua_runtime.globals()


def get_lua_result(lua_interpreter):
    """Helper function to get the result from Lua globals"""
    return lua_interpreter.lua_runtime.globals().result


class TestTimerExtensions:
    """Test timer-related extensions"""

    def test_setTimeout_basic(self, lua_interpreter):
        """Test basic setTimeout functionality"""
        lua_code = """
        local timer_id = _PY.setTimeout(function()
            result = {"timer executed", _G.stored_timer_id}
        end, 100)
        _G.stored_timer_id = timer_id
        """

        create_lua_result_table(lua_interpreter)
        lua_interpreter.execute_code(lua_code)

        # Wait for timer to execute
        time.sleep(0.2)

        result = get_lua_result(lua_interpreter)
        assert result[1] == "timer executed"
        assert isinstance(result[2], int)
        assert result[2] > 0

    def test_clearTimeout(self, lua_interpreter):
        """Test clearTimeout functionality"""
        lua_code = """
        local executed = false
        local timer_id = _PY.setTimeout(function()
            executed = true
        end, 500)

        local cleared = _PY.clearTimeout(timer_id)
        result = {cleared, timer_id}
        """

        create_lua_result_table(lua_interpreter)
        lua_interpreter.execute_code(lua_code)

        # Wait less than the timer duration
        time.sleep(0.3)

        result = get_lua_result(lua_interpreter)
        assert result[1] is True  # Timer was successfully cleared
        assert result[2] > 0

    def test_has_active_timers(self, lua_interpreter):
        """Test has_active_timers function"""
        lua_code = """
        local has_timers = _PY.has_active_timers()

        local timer_id = _PY.setTimeout(function() end, 1000)
        local has_timers_after = _PY.has_active_timers()

        _PY.clearTimeout(timer_id)
        local has_timers_cleared = _PY.has_active_timers()

        result = {has_timers, has_timers_after, has_timers_cleared}
        """

        create_lua_result_table(lua_interpreter)
        lua_interpreter.execute_code(lua_code)

        result = get_lua_result(lua_interpreter)
        assert result[1] is False  # No timers initially
        assert result[2] is True   # Timer active
        assert result[3] is False  # Timer cleared


class TestIOExtensions:
    """Test I/O-related extensions"""

    def test_read_file_success(self, lua_interpreter, sample_lua_file):
        """Test successful file reading"""
        lua_code = f"""
        local content = _PY.read_file("{sample_lua_file}")
        result = {{content ~= nil, string.find(content, "Sample Lua file") ~= nil}}
        """

        create_lua_result_table(lua_interpreter)
        lua_interpreter.execute_code(lua_code)

        result = get_lua_result(lua_interpreter)
        assert result[1] is True
        assert result[2] is True

    def test_read_file_nonexistent(self, lua_interpreter):
        """Test reading non-existent file"""
        lua_code = """
        local content = _PY.read_file("nonexistent_file.lua")
        result = {content == nil}
        """

        create_lua_result_table(lua_interpreter)
        lua_interpreter.execute_code(lua_code)

        result = get_lua_result(lua_interpreter)
        assert result[1] is True

    def test_write_file_success(self, lua_interpreter, temp_file):
        """Test successful file writing"""
        test_content = "Hello, World!"

        lua_code = f"""
        local success = _PY.write_file("{temp_file}", "{test_content}")
        result = {{success}}
        """

        create_lua_result_table(lua_interpreter)
        lua_interpreter.execute_code(lua_code)

        result = get_lua_result(lua_interpreter)
        assert result[1] is True

        # Verify file was written correctly
        with open(temp_file, 'r') as f:
            content = f.read()
        assert content == test_content

    def test_write_file_error(self, lua_interpreter):
        """Test file writing to invalid path"""
        lua_code = """
        local success = _PY.write_file("/invalid/path/file.txt", "content")
        result = {success}
        """

        create_lua_result_table(lua_interpreter)
        lua_interpreter.execute_code(lua_code)

        result = get_lua_result(lua_interpreter)
        assert result[1] is False

    @patch('builtins.input')
    def test_input_lua(self, mock_input, lua_interpreter):
        """Test input_lua function"""
        mock_input.return_value = "test input"

        lua_code = """
        local user_input = _PY.input_lua("Enter something: ")
        result = {user_input}
        """

        create_lua_result_table(lua_interpreter)
        lua_interpreter.execute_code(lua_code)

        result = get_lua_result(lua_interpreter)
        assert result[1] == "test input"
        mock_input.assert_called_once_with("Enter something: ")


class TestSystemExtensions:
    """Test system-related extensions"""

    def test_get_time(self, lua_interpreter):
        """Test get_time function"""
        lua_code = """
        local timestamp = _PY.get_time()
        result = {timestamp > 0, type(timestamp) == "number"}
        """

        create_lua_result_table(lua_interpreter)
        lua_interpreter.execute_code(lua_code)

        result = get_lua_result(lua_interpreter)
        assert result[1] is True
        assert result[2] is True

    def test_sleep_short(self, lua_interpreter):
        """Test sleep function with short duration"""
        start_time = time.time()

        lua_code = """
        _PY.sleep(0.1)
        result = {"sleep completed"}
        """

        create_lua_result_table(lua_interpreter)
        lua_interpreter.execute_code(lua_code)

        elapsed = time.time() - start_time
        assert elapsed >= 0.1

        result = get_lua_result(lua_interpreter)
        assert result[1] == "sleep completed"

    def test_get_python_version(self, lua_interpreter):
        """Test get_python_version function"""
        lua_code = """
        local version = _PY.get_python_version()
        result = {string.find(version, "Python") ~= nil, version}
        """

        create_lua_result_table(lua_interpreter)
        lua_interpreter.execute_code(lua_code)

        result = get_lua_result(lua_interpreter)
        assert result[1] is True
        assert "Python" in result[2]


class TestUtilityExtensions:
    """Test utility extensions"""

    def test_list_extensions(self, lua_interpreter):
        """Test list_extensions function"""
        lua_code = """
        _PY.list_extensions()
        result = {"extensions listed"}
        """

        create_lua_result_table(lua_interpreter)
        lua_interpreter.execute_code(lua_code)

        result = get_lua_result(lua_interpreter)
        assert result[1] == "extensions listed"


class TestLuaEnvironment:
    """Test basic Lua environment setup"""

    def test_basic_lua_execution(self, lua_interpreter):
        """Test basic Lua code execution"""
        lua_code = """
        local x = 10
        local y = 20
        local result = x + y
        _G.test_result = result
        """

        lua_interpreter.execute_code(lua_code)

        # Check if the result is available in Lua globals
        globals = lua_interpreter.lua_runtime.globals()
        assert globals.test_result == 30

    def test_py_table_access(self, lua_interpreter):
        """Test access to _PY table"""
        lua_code = """
        local has_py = _PY ~= nil
        local has_setTimeout = _PY.setTimeout ~= nil
        local has_get_time = _PY.get_time ~= nil
        result = {has_py, has_setTimeout, has_get_time}
        """

        lua_interpreter.lua_runtime.globals()['result'] = None
        lua_interpreter.execute_code(lua_code)

        # Get the result from Lua globals
        globals = lua_interpreter.lua_runtime.globals()
        result = globals.result

        assert result[1] is True
        assert result[2] is True
        assert result[3] is True

    def test_package_path_setup(self, lua_interpreter):
        """Test that package.path is properly set up"""
        lua_code = """
        local path = package.path
        result = {string.find(path, "lua") ~= nil, path}
        """

        lua_interpreter.lua_runtime.globals()['result'] = None
        lua_interpreter.execute_code(lua_code)

        # Get the result from Lua globals
        globals = lua_interpreter.lua_runtime.globals()
        result = globals.result

        assert result[1] is True
        assert "lua" in result[2]
