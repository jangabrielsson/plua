"""
Tests for network extensions (TCP, UDP, HTTP)
"""

import socket
import threading
from unittest.mock import patch, MagicMock


def create_lua_result_table(lua_interpreter):
    """Helper function to create a Lua table for storing test results"""
    lua_interpreter.lua_runtime.globals()['result'] = None
    return lua_interpreter.lua_runtime.globals()


def get_lua_result(lua_interpreter):
    """Helper function to get the result from Lua globals"""
    return lua_interpreter.lua_runtime.globals().result


class TestNetworkUtilityFunctions:
    """Test network utility functions"""

    def test_get_local_ip(self, lua_interpreter):
        """Test get_local_ip function"""
        lua_code = """
        local ip = _PY.get_local_ip()
        result = {ip ~= nil, string.find(ip, "%d+%.%d+%.%d+%.%d+") ~= nil}
        """

        create_lua_result_table(lua_interpreter)
        lua_interpreter.execute_code(lua_code)

        result = get_lua_result(lua_interpreter)
        assert result[1] is True
        assert result[2] is True

    def test_is_port_available(self, lua_interpreter):
        """Test is_port_available function"""
        lua_code = """
        local available = _PY.is_port_available(9999)
        result = {available}
        """

        create_lua_result_table(lua_interpreter)
        lua_interpreter.execute_code(lua_code)

        result = get_lua_result(lua_interpreter)
        assert isinstance(result[1], bool)

    def test_get_hostname(self, lua_interpreter):
        """Test get_hostname function"""
        lua_code = """
        local hostname = _PY.get_hostname()
        result = {hostname ~= nil, hostname ~= ""}
        """

        create_lua_result_table(lua_interpreter)
        lua_interpreter.execute_code(lua_code)

        result = get_lua_result(lua_interpreter)
        assert result[1] is True
        assert result[2] is True


class TestSynchronousTCPFunctions:
    """Test synchronous TCP functions"""

    def test_tcp_connect_sync_success(self, lua_interpreter):
        """Test successful TCP connection"""
        # Create a simple test server
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(('localhost', 0))  # Let OS choose port
        server_socket.listen(1)
        port = server_socket.getsockname()[1]

        try:
            lua_code = f"""
            local success, conn_id, message = _PY.tcp_connect_sync("localhost", {port})
            result = {{success, conn_id, message}}
            """

            create_lua_result_table(lua_interpreter)
            lua_interpreter.execute_code(lua_code)

            result = get_lua_result(lua_interpreter)
            assert result[1] is True
            assert isinstance(result[2], int)
            assert result[2] > 0
            assert "Connected" in result[3]

        finally:
            server_socket.close()

    def test_tcp_connect_sync_failure(self, lua_interpreter):
        """Test TCP connection failure"""
        lua_code = """
        local success, conn_id, message = _PY.tcp_connect_sync("invalid-host", 9999)
        result = {success, conn_id, message}
        """

        create_lua_result_table(lua_interpreter)
        lua_interpreter.execute_code(lua_code)

        result = get_lua_result(lua_interpreter)
        assert result[1] is False
        assert result[2] is None
        assert "error" in result[3].lower()

    def test_tcp_write_read_sync(self, lua_interpreter):
        """Test TCP write and read operations"""
        # Create a simple echo server
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(('localhost', 0))
        server_socket.listen(1)
        port = server_socket.getsockname()[1]

        def echo_server():
            client, addr = server_socket.accept()
            data = client.recv(1024)
            client.send(data)
            client.close()

        server_thread = threading.Thread(target=echo_server)
        server_thread.daemon = True
        server_thread.start()

        try:
            lua_code = f"""
            local success, conn_id, message = _PY.tcp_connect_sync("localhost", {port})
            if success then
                local write_success, bytes_written, write_msg = _PY.tcp_write_sync(conn_id, "Hello, World!")
                local read_success, data, read_msg = _PY.tcp_read_sync(conn_id, "*a")
                _PY.tcp_close_sync(conn_id)
                result = {{write_success, bytes_written, read_success, data}}
            end
            """

            create_lua_result_table(lua_interpreter)
            lua_interpreter.execute_code(lua_code)

            result = get_lua_result(lua_interpreter)
            assert result[1] is True
            assert result[2] == 13  # "Hello, World!" length
            assert result[3] is True
            assert result[4] == "Hello, World!"

        finally:
            server_socket.close()

    def test_tcp_timeout_functions(self, lua_interpreter):
        """Test TCP timeout getter and setter"""
        # Create a simple test server
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(('localhost', 0))
        server_socket.listen(1)
        port = server_socket.getsockname()[1]

        try:
            lua_code = f"""
            local success, conn_id, message = _PY.tcp_connect_sync("localhost", {port})
            if success then
                local set_success, set_msg = _PY.tcp_set_timeout_sync(conn_id, 5.0)
                local get_success, timeout, get_msg = _PY.tcp_get_timeout_sync(conn_id)
                _PY.tcp_close_sync(conn_id)
                result = {{set_success, get_success, timeout}}
            end
            """

            create_lua_result_table(lua_interpreter)
            lua_interpreter.execute_code(lua_code)

            result = get_lua_result(lua_interpreter)
            assert result[1] is True
            assert result[2] is True
            assert result[3] == 5.0

        finally:
            server_socket.close()


class TestHTTPFunctions:
    """Test HTTP request functions"""

    @patch('urllib.request.urlopen')
    def test_http_request_sync_success(self, mock_urlopen, lua_interpreter):
        """Test successful HTTP request"""
        # Mock the HTTP response
        mock_response = MagicMock()
        mock_response.getcode.return_value = 200
        mock_response.read.return_value = b"Hello, World!"
        mock_response.headers = {"Content-Type": "text/plain"}
        mock_response.url = "http://example.com"
        mock_urlopen.return_value.__enter__.return_value = mock_response

        lua_code = """
        local response = _PY.http_request_sync("http://example.com")
        result = {response.code, response.body, response.headers["Content-Type"], response.url}
        """

        create_lua_result_table(lua_interpreter)
        lua_interpreter.execute_code(lua_code)

        result = get_lua_result(lua_interpreter)
        assert result[1] == 200
        assert result[2] == "Hello, World!"
        assert result[3] == "text/plain"
        assert result[4] == "http://example.com"

    @patch('urllib.request.urlopen')
    def test_http_request_sync_with_table(self, mock_urlopen, lua_interpreter):
        """Test HTTP request with table parameters"""
        # Mock the HTTP response
        mock_response = MagicMock()
        mock_response.getcode.return_value = 200
        mock_response.read.return_value = b"POST response"
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.url = "http://example.com/api"
        mock_urlopen.return_value.__enter__.return_value = mock_response

        lua_code = """
        local request = {
            url = "http://example.com/api",
            method = "POST",
            headers = {["Content-Type"] = "application/json"},
            body = '{"key": "value"}'
        }
        local response = _PY.http_request_sync(request)
        result = {response.code, response.body}
        """

        create_lua_result_table(lua_interpreter)
        lua_interpreter.execute_code(lua_code)

        result = get_lua_result(lua_interpreter)
        assert result[1] == 200
        assert result[2] == "POST response"

    @patch('urllib.request.urlopen')
    def test_http_request_sync_error(self, mock_urlopen, lua_interpreter):
        """Test HTTP request with error"""
        # Mock HTTP error
        from urllib.error import HTTPError
        mock_urlopen.side_effect = HTTPError("http://example.com", 404, "Not Found", {}, None)

        lua_code = """
        local response = _PY.http_request_sync("http://example.com")
        result = {response.code, response.error}
        """

        create_lua_result_table(lua_interpreter)
        lua_interpreter.execute_code(lua_code)

        result = get_lua_result(lua_interpreter)
        assert result[1] == 404
        assert result[2] is True


class TestNetworkManager:
    """Test network manager functionality"""

    def test_has_active_network_operations(self, lua_interpreter):
        """Test has_active_network_operations function"""
        lua_code = """
        local has_ops = _PY.has_active_network_operations()
        result = {has_ops}
        """

        create_lua_result_table(lua_interpreter)
        lua_interpreter.execute_code(lua_code)

        result = get_lua_result(lua_interpreter)
        assert isinstance(result[1], bool)


class TestLuaModuleLoading:
    """Test Lua module loading functionality"""

    def test_load_library_success(self, lua_interpreter, temp_dir):
        """Test successful library loading"""
        # Create a simple Lua module
        module_file = f"{temp_dir}/test_module.lua"
        with open(module_file, 'w') as f:
            f.write("""
local test_module = {}
test_module.hello = function() return "Hello from module" end
return test_module
""")

        # Add the temp directory to package.path
        lua_code = f"""
        package.path = package.path .. ";{temp_dir}/?.lua"
        test_module = require('test_module')
        result = {{test_module.hello()}}
        """

        create_lua_result_table(lua_interpreter)
        lua_interpreter.execute_code(lua_code)

        result = get_lua_result(lua_interpreter)
        assert result[1] == "Hello from module"

    def test_load_library_failure(self, lua_interpreter):
        """Test library loading failure"""
        lua_code = """
        local success = pcall(function()
            require('nonexistent_module')
        end)
        result = {success}
        """

        create_lua_result_table(lua_interpreter)
        lua_interpreter.execute_code(lua_code)

        result = get_lua_result(lua_interpreter)
        assert result[1] is False
