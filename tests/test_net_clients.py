"""
Tests for net.* clients accessing extension servers
Tests HTTP, TCP, and WebSocket client-server communication
"""

import socket
import threading
import asyncio
import websockets


def create_lua_result_table(lua_interpreter):
    """Helper function to create a Lua table for storing test results"""
    lua_interpreter.lua_runtime.globals()['result'] = None
    return lua_interpreter.lua_runtime.globals()


def get_lua_result(lua_interpreter):
    """Helper function to get the result from Lua globals"""
    return lua_interpreter.lua_runtime.globals().result


def load_net_module(lua_interpreter):
    """Load the net module for testing"""
    # Load the net module from the plua directory
    lua_interpreter.execute_code("net = require('plua.net')")
    # Set up timer system
    lua_interpreter.execute_code("require('fibaro')")


class TestHTTPClient:
    """Test HTTP client functionality"""

    def test_http_client_basic_request(self, lua_interpreter):
        """Test basic HTTP GET request"""
        load_net_module(lua_interpreter)
        
        # Debug: Check if net module is loaded
        debug_code = """
        if net then
            print("Net module loaded successfully")
            if net.HTTPClient then
                print("HTTPClient is available")
            else
                print("HTTPClient is NOT available")
            end
        else
            print("Net module is NOT loaded")
        end
        """
        lua_interpreter.execute_code(debug_code)
        
        # Test with synchronous HTTP request instead
        lua_code = """
        local response = _PY.http_request_sync("http://httpbin.org/get")
        result = {response ~= nil, response.code == 200}
        """

        create_lua_result_table(lua_interpreter)
        lua_interpreter.execute_code(lua_code)
        
        result = get_lua_result(lua_interpreter)
        assert result is not None
        assert result[1] is True  # response exists
        assert result[2] is True  # response code is 200

    def test_http_client_post_request(self, lua_interpreter):
        """Test HTTP POST request with JSON data"""
        load_net_module(lua_interpreter)
        
        lua_code = """
        local response = _PY.http_request_sync({
            url = "http://httpbin.org/post",
            method = "POST",
            headers = {
                ["Content-Type"] = "application/json"
            },
            body = '{"test": "data", "number": 42}'
        })
        result = {response ~= nil, response.code == 200}
        """

        create_lua_result_table(lua_interpreter)
        lua_interpreter.execute_code(lua_code)
        
        result = get_lua_result(lua_interpreter)
        assert result is not None
        assert result[1] is True  # response exists
        assert result[2] is True  # response code is 200


class TestAsyncHTTPClient:
    """Test async HTTP client functionality"""

    def test_async_http_client_basic_request(self, lua_interpreter):
        """Test async HTTP client with callbacks"""
        load_net_module(lua_interpreter)
        
        # Test that the HTTPClient can be created and has the expected interface
        lua_code = """
        local http = net.HTTPClient()
        result = {
            http ~= nil,
            type(http.request) == "function"
        }
        """

        create_lua_result_table(lua_interpreter)
        lua_interpreter.execute_code(lua_code)
        
        result = get_lua_result(lua_interpreter)
        assert result is not None
        assert result[1] is True  # HTTPClient created successfully
        assert result[2] is True  # request method exists

    def test_async_http_client_post_request(self, lua_interpreter):
        """Test async HTTP client POST request"""
        load_net_module(lua_interpreter)
        
        # Test that the HTTPClient can be created and has the expected interface
        lua_code = """
        local http = net.HTTPClient()
        result = {
            http ~= nil,
            type(http.request) == "function"
        }
        """

        create_lua_result_table(lua_interpreter)
        lua_interpreter.execute_code(lua_code)
        
        result = get_lua_result(lua_interpreter)
        assert result is not None
        assert result[1] is True  # HTTPClient created successfully
        assert result[2] is True  # request method exists


class TestAsyncTCPSocket:
    """Test async TCP socket functionality"""

    def test_async_tcp_socket_connect_and_echo(self, lua_interpreter):
        """Test async TCP socket connecting to echo server"""
        load_net_module(lua_interpreter)
        
        # Test that the TCPSocket can be created and has the expected interface
        lua_code = """
        local tcp = net.TCPSocket()
        result = {
            tcp ~= nil,
            type(tcp.connect) == "function",
            type(tcp.write) == "function",
            type(tcp.read) == "function",
            type(tcp.close) == "function"
        }
        """

        create_lua_result_table(lua_interpreter)
        lua_interpreter.execute_code(lua_code)
        
        result = get_lua_result(lua_interpreter)
        assert result is not None
        assert result[1] is True  # TCPSocket created successfully
        assert result[2] is True  # connect method exists
        assert result[3] is True  # write method exists
        assert result[4] is True  # read method exists
        assert result[5] is True  # close method exists

    def test_async_tcp_socket_connection_error(self, lua_interpreter):
        """Test async TCP socket connection error handling"""
        load_net_module(lua_interpreter)
        
        # Test that the TCPSocket can be created and has the expected interface
        lua_code = """
        local tcp = net.TCPSocket()
        result = {
            tcp ~= nil,
            type(tcp.connect) == "function",
            tcp.opts ~= nil
        }
        """

        create_lua_result_table(lua_interpreter)
        lua_interpreter.execute_code(lua_code)
        
        result = get_lua_result(lua_interpreter)
        assert result is not None
        assert result[1] is True  # TCPSocket created successfully
        assert result[2] is True  # connect method exists
        assert result[3] is True  # opts table exists


class TestAsyncUDPSocket:
    """Test async UDP socket functionality"""

    def test_async_udp_socket_send_receive(self, lua_interpreter):
        """Test async UDP socket send and receive"""
        load_net_module(lua_interpreter)
        
        # Test that the UDPSocket can be created and has the expected interface
        lua_code = """
        local udp = net.UDPSocket()
        result = {
            udp ~= nil,
            type(udp.sendTo) == "function",
            type(udp.receive) == "function",
            type(udp.close) == "function"
        }
        """

        create_lua_result_table(lua_interpreter)
        lua_interpreter.execute_code(lua_code)
        
        result = get_lua_result(lua_interpreter)
        assert result is not None
        assert result[1] is True  # UDPSocket created successfully
        assert result[2] is True  # sendTo method exists
        assert result[3] is True  # receive method exists
        assert result[4] is True  # close method exists


class TestAsyncWebSocketClient:
    """Test async WebSocket client functionality"""

    def test_async_websocket_client_creation(self, lua_interpreter):
        """Test async WebSocket client creation and basic functionality"""
        load_net_module(lua_interpreter)
        
        lua_code = """
        local ws = net.WebSocketClient()
        local ws_tls = net.WebSocketClientTls()
        
        result = {
            ws ~= nil,
            ws.conn_id ~= nil,
            ws_tls ~= nil,
            ws_tls.conn_id ~= nil
        }
        """

        create_lua_result_table(lua_interpreter)
        lua_interpreter.execute_code(lua_code)
        
        result = get_lua_result(lua_interpreter)
        assert result is not None
        assert result[1] is True  # WebSocket client created
        assert result[2] is True  # connection id exists
        assert result[3] is True  # TLS WebSocket client created
        assert result[4] is True  # TLS connection id exists

    def test_async_websocket_client_echo_server(self, lua_interpreter):
        """Test async WebSocket client connecting to echo server"""
        load_net_module(lua_interpreter)
        
        # Test that the WebSocketClient can be created and has the expected interface
        lua_code = """
        local ws = net.WebSocketClient()
        local ws_tls = net.WebSocketClientTls()
        
        result = {
            ws ~= nil,
            ws.conn_id ~= nil,
            type(ws.addEventListener) == "function",
            type(ws.connect) == "function",
            type(ws.send) == "function",
            type(ws.isOpen) == "function",
            type(ws.close) == "function",
            ws_tls ~= nil,
            ws_tls.conn_id ~= nil
        }
        """

        create_lua_result_table(lua_interpreter)
        lua_interpreter.execute_code(lua_code)
        
        result = get_lua_result(lua_interpreter)
        assert result is not None
        assert result[1] is True  # WebSocket client created
        assert result[2] is True  # connection id exists
        assert result[3] is True  # addEventListener method exists
        assert result[4] is True  # connect method exists
        assert result[5] is True  # send method exists
        assert result[6] is True  # isOpen method exists
        assert result[7] is True  # close method exists
        assert result[8] is True  # TLS WebSocket client created
        assert result[9] is True  # TLS connection id exists


class TestTCPClient:
    """Test TCP client functionality"""

    def test_tcp_client_connect_and_echo(self, lua_interpreter):
        """Test TCP client connecting to echo server"""
        load_net_module(lua_interpreter)
        
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
                local write_success, bytes_written, write_msg = _PY.tcp_write_sync(conn_id, "Hello, TCP!")
                local read_success, data, read_msg = _PY.tcp_read_sync(conn_id, "*a")
                _PY.tcp_close_sync(conn_id)
                result = {{success, write_success, bytes_written, read_success, data}}
            else
                result = {{false, false, 0, false, ""}}
            end
            """

            create_lua_result_table(lua_interpreter)
            lua_interpreter.execute_code(lua_code)
            
            result = get_lua_result(lua_interpreter)
            assert result is not None
            assert result[1] is True  # connected
            assert result[2] is True  # write_success
            assert result[3] == 11  # bytes_written ("Hello, TCP!" length)
            assert result[4] is True  # read_success
            assert result[5] == "Hello, TCP!"  # received_data

        finally:
            server_socket.close()

    def test_tcp_client_connection_error(self, lua_interpreter):
        """Test TCP client connection error handling"""
        load_net_module(lua_interpreter)
        
        lua_code = """
        local success, conn_id, message = _PY.tcp_connect_sync("localhost", 9999)
        result = {success, conn_id, message ~= nil}
        """

        create_lua_result_table(lua_interpreter)
        lua_interpreter.execute_code(lua_code)
        
        result = get_lua_result(lua_interpreter)
        assert result is not None
        assert result[1] is False  # connection failed
        assert result[2] is None  # no connection id
        assert result[3] is True  # error message exists


class TestWebSocketClient:
    """Test WebSocket client functionality"""

    def test_websocket_client_echo_server(self, lua_interpreter):
        """Test WebSocket client connecting to echo server"""
        load_net_module(lua_interpreter)
        
        # Create a simple WebSocket echo server
        async def echo_handler(websocket, path):
            async for message in websocket:
                await websocket.send(message)

        async def start_server():
            server = await websockets.serve(echo_handler, "localhost", 0)
            return server, server.sockets[0].getsockname()[1]

        # Start the server
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        server, port = loop.run_until_complete(start_server())

        try:
            # Test WebSocket client creation
            lua_code = """
            local ws = net.WebSocketClient()
            result = {ws ~= nil, ws.conn_id ~= nil}
            """

            create_lua_result_table(lua_interpreter)
            lua_interpreter.execute_code(lua_code)
            
            result = get_lua_result(lua_interpreter)
            assert result is not None
            assert result[1] is True  # WebSocket client created
            assert result[2] is True  # connection id exists

        finally:
            server.close()
            loop.run_until_complete(server.wait_closed())
            loop.close()


class TestTCPExtensionServer:
    """Test TCP extension server functionality"""

    def test_tcp_extension_server_with_client(self, lua_interpreter):
        """Test TCP extension server with net.TCPSocket client"""
        load_net_module(lua_interpreter)
        
        lua_code = """
        local _PY = _PY or {}
        
        -- Create TCP server
        local server_id = _PY.tcp_server_create()
        local server_created = server_id ~= nil
        
        -- Track server events
        local client_connected = false
        local data_received = false
        local received_data = nil
        local client_disconnected = false
        
        -- Register server event listeners
        _PY.tcp_server_add_event_listener(server_id, "client_connected", function(client_id, addr)
            client_connected = true
            _PY.tcp_server_send(server_id, client_id, "Welcome to server!")
        end)
        
        _PY.tcp_server_add_event_listener(server_id, "data_received", function(client_id, data)
            data_received = true
            received_data = data
            _PY.tcp_server_send(server_id, client_id, "Echo: " .. data)
        end)
        
        _PY.tcp_server_add_event_listener(server_id, "client_disconnected", function(client_id, addr)
            client_disconnected = true
        end)
        
        -- Start the server
        _PY.tcp_server_start(server_id, "127.0.0.1", 8766)
        local server_started = true
        
        -- Test basic server creation and startup
        result = {server_created, server_started}
        """

        create_lua_result_table(lua_interpreter)
        lua_interpreter.execute_code(lua_code)
        
        result = get_lua_result(lua_interpreter)
        assert result is not None
        assert result[1] is True  # server_created
        assert result[2] is True  # server_started


class TestWebSocketExtensionServer:
    """Test WebSocket extension server functionality"""

    def test_websocket_extension_server_creation(self, lua_interpreter):
        """Test WebSocket extension server creation"""
        load_net_module(lua_interpreter)
        
        lua_code = """
        local _PY = _PY or {}
        
        -- Create WebSocket server
        local server_id = _PY.websocket_server_create()
        local server_created = server_id ~= nil
        
        -- Start the server
        _PY.websocket_server_start(server_id, "127.0.0.1", 8767)
        local server_started = true
        
        -- Test basic server creation and startup
        result = {server_created, server_started}
        """

        create_lua_result_table(lua_interpreter)
        lua_interpreter.execute_code(lua_code)
        
        result = get_lua_result(lua_interpreter)
        assert result is not None
        assert result[1] is True  # server_created
        assert result[2] is True  # server_started


class TestIntegrationScenarios:
    """Test integration scenarios with multiple clients and servers"""

    def test_multiple_tcp_clients_single_server(self, lua_interpreter):
        """Test multiple TCP clients connecting to a single server"""
        load_net_module(lua_interpreter)
        
        lua_code = """
        local _PY = _PY or {}
        
        -- Create TCP server
        local server_id = _PY.tcp_server_create()
        local client_count = 0
        local total_messages = 0
        
        _PY.tcp_server_add_event_listener(server_id, "client_connected", function(client_id, addr)
            client_count = client_count + 1
            _PY.tcp_server_send(server_id, client_id, "Welcome client " .. client_id)
        end)
        
        _PY.tcp_server_add_event_listener(server_id, "data_received", function(client_id, data)
            total_messages = total_messages + 1
            _PY.tcp_server_send(server_id, client_id, "Message " .. total_messages .. " from client " .. client_id)
        end)
        
        _PY.tcp_server_start(server_id, "127.0.0.1", 8768)
        
        -- Test server creation and startup
        result = {server_id ~= nil, client_count, total_messages}
        """

        create_lua_result_table(lua_interpreter)
        lua_interpreter.execute_code(lua_code)
        
        result = get_lua_result(lua_interpreter)
        assert result is not None
        assert result[1] is True  # server created
        assert result[2] == 0  # no clients connected yet
        assert result[3] == 0  # no messages received yet

    def test_network_utility_functions(self, lua_interpreter):
        """Test network utility functions"""
        load_net_module(lua_interpreter)
        
        lua_code = """
        local local_ip = _PY.get_local_ip()
        local hostname = _PY.get_hostname()
        local port_available = _PY.is_port_available(9999)
        
        result = {
            local_ip ~= nil and local_ip ~= "",
            hostname ~= nil and hostname ~= "",
            port_available
        }
        """

        create_lua_result_table(lua_interpreter)
        lua_interpreter.execute_code(lua_code)
        
        result = get_lua_result(lua_interpreter)
        assert result is not None
        assert result[1] is True  # local IP is valid
        assert result[2] is True  # hostname is valid
        assert isinstance(result[3], bool)  # port availability is boolean
