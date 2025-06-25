"""
Tests for the main PLua interpreter
"""

from unittest.mock import patch


class TestPLuaInterpreter:
    """Test the main PLua interpreter class"""

    def test_interpreter_initialization(self, lua_interpreter):
        """Test interpreter initialization"""
        assert lua_interpreter.lua_runtime is not None
        assert lua_interpreter.debug is False

    def test_debug_interpreter_initialization(self, debug_lua_interpreter):
        """Test debug interpreter initialization"""
        assert debug_lua_interpreter.lua_runtime is not None
        assert debug_lua_interpreter.debug is True

    def test_debug_print(self, debug_lua_interpreter, capsys):
        """Test debug print functionality"""
        debug_lua_interpreter.debug_print("Test debug message")
        captured = capsys.readouterr()
        assert "DEBUG: Test debug message" in captured.err

    def test_debug_print_disabled(self, lua_interpreter, capsys):
        """Test debug print when debug is disabled"""
        lua_interpreter.debug_print("Test debug message")
        captured = capsys.readouterr()
        assert "DEBUG: Test debug message" not in captured.err

    def test_basic_lua_execution(self, lua_interpreter):
        """Test basic Lua code execution"""
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

    def test_lua_execution_with_error(self, lua_interpreter):
        """Test Lua code execution with syntax error"""
        lua_code = """
        local x = 10
        local y = 20
        local result = x + y
        -- Syntax error: missing closing brace
        if x > 5 then
            print("x is greater than 5"
        """

        success = lua_interpreter.execute_code(lua_code)
        assert success is False

    def test_execute_file_success(self, lua_interpreter, sample_lua_file):
        """Test successful file execution"""
        success = lua_interpreter.execute_file(sample_lua_file)
        assert success is True

    def test_execute_file_nonexistent(self, lua_interpreter):
        """Test file execution with non-existent file"""
        success = lua_interpreter.execute_file("nonexistent_file.lua")
        assert success is False

    def test_execute_file_with_syntax_error(self, lua_interpreter, error_lua_file):
        """Test file execution with syntax error"""
        success = lua_interpreter.execute_file(error_lua_file)
        assert success is False

    def test_execute_code_with_filename(self, lua_interpreter):
        """Test execute_code_with_filename method"""
        lua_code = """
        local x = 10
        local y = 20
        local result = x + y
        _G.test_result = result
        """

        success = lua_interpreter.execute_code_with_filename(lua_code, "test_file.lua")
        assert success is True

        # Check if the result is available in Lua globals
        globals = lua_interpreter.lua_runtime.globals()
        assert globals.test_result == 30

    def test_load_library_success(self, lua_interpreter, temp_dir):
        """Test successful library loading"""
        # Create a simple Lua module
        module_file = f"{temp_dir}/test_lib.lua"
        with open(module_file, 'w') as f:
            f.write("""
local test_lib = {}
test_lib.hello = function() return "Hello from library" end
return test_lib
""")

        # Add the temp directory to package.path
        lua_interpreter.lua_runtime.execute(f'package.path = package.path .. ";{temp_dir}/?.lua"')

        success = lua_interpreter.load_library("test_lib")
        assert success is True

        # Verify the library is loaded
        globals = lua_interpreter.lua_runtime.globals()
        assert hasattr(globals, 'test_lib')
        assert globals.test_lib.hello() == "Hello from library"

    def test_load_library_failure(self, lua_interpreter):
        """Test library loading failure"""
        success = lua_interpreter.load_library("nonexistent_library")
        assert success is False

    def test_load_libraries(self, lua_interpreter, temp_dir):
        """Test loading multiple libraries"""
        # Create test libraries
        lib1_file = f"{temp_dir}/lib1.lua"
        lib2_file = f"{temp_dir}/lib2.lua"

        with open(lib1_file, 'w') as f:
            f.write("""
local lib1 = {}
lib1.func1 = function() return "lib1" end
return lib1
""")

        with open(lib2_file, 'w') as f:
            f.write("""
local lib2 = {}
lib2.func2 = function() return "lib2" end
return lib2
""")

        # Add the temp directory to package.path
        lua_interpreter.lua_runtime.execute(f'package.path = package.path .. ";{temp_dir}/?.lua"')

        success = lua_interpreter.load_libraries(["lib1", "lib2"])
        assert success is True

        # Verify both libraries are loaded
        globals = lua_interpreter.lua_runtime.globals()
        assert hasattr(globals, 'lib1')
        assert hasattr(globals, 'lib2')
        assert globals.lib1.func1() == "lib1"
        assert globals.lib2.func2() == "lib2"

    def test_load_libraries_partial_failure(self, lua_interpreter, temp_dir):
        """Test loading libraries with some failures"""
        # Create one valid library
        lib1_file = f"{temp_dir}/lib1.lua"
        with open(lib1_file, 'w') as f:
            f.write("""
local lib1 = {}
lib1.func1 = function() return "lib1" end
return lib1
""")

        # Add the temp directory to package.path
        lua_interpreter.lua_runtime.execute(f'package.path = package.path .. ";{temp_dir}/?.lua"')

        success = lua_interpreter.load_libraries(["lib1", "nonexistent_lib"])
        assert success is False

    def test_escape_lua_string(self, lua_interpreter):
        """Test Lua string escaping"""
        test_string = "Hello\\World"
        escaped = lua_interpreter._escape_lua_string(test_string)
        assert escaped == "Hello\\\\World"

    def test_has_active_operations(self, lua_interpreter):
        """Test has_active_operations method"""
        has_ops = lua_interpreter._has_active_operations()
        assert isinstance(has_ops, bool)

    @patch('extensions.core.timer_manager')
    @patch('extensions.network_extensions.network_manager')
    def test_wait_for_active_operations(self, mock_network_manager, mock_timer_manager, lua_interpreter):
        """Test wait_for_active_operations method"""
        # Mock the managers to return False (no active operations)
        mock_timer_manager.has_active_timers.return_value = False
        mock_network_manager.has_active_operations.return_value = False

        lua_interpreter.wait_for_active_operations()

        # Verify the managers were called
        mock_timer_manager.has_active_timers.assert_called()
        mock_network_manager.has_active_operations.assert_called()

    @patch('builtins.input')
    def test_run_interactive_exit(self, mock_input, lua_interpreter):
        """Test interactive mode exit"""
        mock_input.return_value = "exit"

        lua_interpreter.run_interactive()

        mock_input.assert_called_once()

    @patch('builtins.input')
    def test_run_interactive_help(self, mock_input, lua_interpreter, capsys):
        """Test interactive mode help command"""
        mock_input.side_effect = ["help", "exit"]

        lua_interpreter.run_interactive()

        captured = capsys.readouterr()
        assert "Available commands:" in captured.out

    @patch('builtins.input')
    def test_run_interactive_code_execution(self, mock_input, lua_interpreter):
        """Test interactive mode code execution"""
        mock_input.side_effect = ["print('Hello, World!')", "exit"]

        lua_interpreter.run_interactive()

        # Verify the code was executed (we can't easily capture print output in tests)
        assert mock_input.call_count == 2


class TestPLuaEnvironment:
    """Test PLua environment setup"""

    def test_py_table_availability(self, lua_interpreter):
        """Test that _PY table is available with all expected functions"""
        globals = lua_interpreter.lua_runtime.globals()

        # Check that _PY table exists
        assert hasattr(globals, '_PY')

        # Check for core functions
        assert hasattr(globals._PY, 'setTimeout')
        assert hasattr(globals._PY, 'clearTimeout')
        assert hasattr(globals._PY, 'has_active_timers')
        assert hasattr(globals._PY, 'read_file')
        assert hasattr(globals._PY, 'write_file')
        assert hasattr(globals._PY, 'get_time')
        assert hasattr(globals._PY, 'sleep')
        assert hasattr(globals._PY, 'get_python_version')
        assert hasattr(globals._PY, 'list_extensions')

        # Check for network functions
        assert hasattr(globals._PY, 'tcp_connect_sync')
        assert hasattr(globals._PY, 'tcp_write_sync')
        assert hasattr(globals._PY, 'tcp_read_sync')
        assert hasattr(globals._PY, 'tcp_close_sync')
        assert hasattr(globals._PY, 'http_request_sync')
        assert hasattr(globals._PY, 'get_local_ip')
        assert hasattr(globals._PY, 'is_port_available')
        assert hasattr(globals._PY, 'get_hostname')

    def test_package_path_setup(self, lua_interpreter):
        """Test that package.path is properly configured"""
        globals = lua_interpreter.lua_runtime.globals()

        # Check that package.path contains the lua directory
        package_path = str(globals.package.path)
        assert "lua" in package_path

    def test_input_function_availability(self, lua_interpreter):
        """Test that input function is available"""
        globals = lua_interpreter.lua_runtime.globals()
        assert hasattr(globals, 'input')
        assert callable(globals.input)


class TestPLuaErrorHandling:
    """Test PLua error handling"""

    def test_lua_syntax_error_handling(self, lua_interpreter):
        """Test handling of Lua syntax errors"""
        lua_code = """
        local x = 10
        local y = 20
        -- Missing closing brace
        if x > 5 then
            print("x is greater than 5"
        """

        success = lua_interpreter.execute_code(lua_code)
        assert success is False

    def test_lua_runtime_error_handling(self, lua_interpreter):
        """Test handling of Lua runtime errors"""
        lua_code = """
        local x = nil
        local y = x + 10  -- Attempt to add nil
        """

        success = lua_interpreter.execute_code(lua_code)
        assert success is False

    def test_file_not_found_handling(self, lua_interpreter):
        """Test handling of file not found errors"""
        success = lua_interpreter.execute_file("nonexistent_file.lua")
        assert success is False

    def test_library_not_found_handling(self, lua_interpreter):
        """Test handling of library not found errors"""
        success = lua_interpreter.load_library("nonexistent_library")
        assert success is False
