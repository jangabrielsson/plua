"""
Tests for network functionality (HTTP, TCP, UDP)
"""

import pytest
import asyncio
import aiohttp
from aiohttp import web
from plua.runtime import LuaAsyncRuntime


class TestNetworkFunctionality:
    """Test cases for network operations"""
    
    async def create_test_server(self, port=8999):
        """Create a simple test HTTP server"""
        async def hello_handler(request):
            return web.json_response({"message": "Hello from test server", "status": "ok"})
        
        async def echo_handler(request):
            data = await request.text()
            return web.json_response({"echo": data, "method": request.method})
        
        async def status_handler(request):
            return web.json_response({"status": "running"})
        
        app = web.Application()
        app.router.add_get('/hello', hello_handler)
        app.router.add_post('/echo', echo_handler)
        app.router.add_get('/status', status_handler)
        
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, 'localhost', port)
        await site.start()
        return runner
    
    @pytest.mark.asyncio
    async def test_http_get_request(self):
        """Test HTTP GET request functionality"""
        # Start test server
        server = await self.create_test_server(8999)
        
        try:
            runtime = LuaAsyncRuntime()
            runtime.initialize_lua()
            
            # Test HTTP GET request
            script = """
            response_received = false  -- Global variables
            response_data = nil
            response_status = nil
            
            local client = net.HTTPClient()
            client:request("http://localhost:8999/hello", {
                options = { method = "GET" },
                success = function(response)
                    response_received = true
                    response_data = response.data
                    response_status = response.status
                end,
                error = function(status)
                    response_received = true
                    response_status = status
                end
            })
            
            return response_received
            """
            
            # Execute the request
            result = runtime.interpreter.lua.execute(script)
            assert result == False  # Response not received yet
            
            # Wait for the async request to complete
            await asyncio.sleep(1.0)
            
            # Check that response was received
            response_received = runtime.interpreter.lua.eval("response_received")
            response_status = runtime.interpreter.lua.eval("response_status")
            
            assert response_received == True
            assert response_status == 200
            
        finally:
            # Clean up server
            await server.cleanup()
    
    @pytest.mark.asyncio
    async def test_http_post_request(self):
        """Test HTTP POST request with data"""
        # Start test server
        server = await self.create_test_server(9000)
        
        try:
            runtime = LuaAsyncRuntime()
            runtime.initialize_lua()
            
            script = """
            response_received = false  -- Global variables
            response_data = nil
            echo_data = nil
            
            local client = net.HTTPClient()
            client:request("http://localhost:9000/echo", {
                options = { 
                    method = "POST",
                    data = "test_payload",
                    headers = { ["Content-Type"] = "text/plain" }
                },
                success = function(response)
                    response_received = true
                    response_data = response.data
                    if response_data then
                        local decoded = json.decode(response_data)
                        if decoded then
                            echo_data = decoded.echo
                        end
                    end
                end,
                error = function(status)
                    response_received = true
                end
            })
            """
            
            runtime.interpreter.lua.execute(script)
            
            # Wait for the async request to complete
            await asyncio.sleep(1.0)
            
            # Check results
            response_received = runtime.interpreter.lua.eval("response_received")
            echo_data = runtime.interpreter.lua.eval("echo_data")
            
            assert response_received == True
            assert echo_data == "test_payload"
            
        finally:
            await server.cleanup()
    
    @pytest.mark.asyncio
    async def test_http_error_handling(self):
        """Test HTTP error handling for non-existent endpoints"""
        runtime = LuaAsyncRuntime()
        runtime.initialize_lua()
        
        script = """
        error_received = false  -- Global variables
        error_status = nil
        
        local client = net.HTTPClient()
        client:request("http://192.0.2.1:12345/nonexistent", {
            options = { 
                method = "GET",
                timeout = 1  -- Short timeout to force error quickly
            },
            success = function(response)
                -- Should not reach here for invalid address
            end,
            error = function(status)
                error_received = true
                error_status = status
            end
        })
        """
        
        runtime.interpreter.lua.execute(script)
        
        # Wait for the request to fail
        await asyncio.sleep(2.0)
        
        # Check that error was handled
        error_received = runtime.interpreter.lua.eval("error_received")
        assert error_received == True
    
    @pytest.mark.asyncio
    async def test_tcp_socket_basic(self):
        """Test basic TCP socket functionality"""
        runtime = LuaAsyncRuntime()
        runtime.initialize_lua()
        
        # Test TCP socket creation
        script = """
        local socket = net.TCPSocket({ timeout = 5000 })
        return type(socket)
        """
        
        result = runtime.interpreter.lua.execute(script)
        assert result == "table"  # Socket should be a table/object
    
    @pytest.mark.asyncio
    async def test_udp_socket_basic(self):
        """Test basic UDP socket functionality"""
        runtime = LuaAsyncRuntime()
        runtime.initialize_lua()
        
        # Test UDP socket creation
        script = """
        local socket = net.UDPSocket({ timeout = 5000 })
        return type(socket)
        """
        
        result = runtime.interpreter.lua.execute(script)
        assert result == "table"  # Socket should be a table/object
    
    @pytest.mark.asyncio
    async def test_network_timeout_handling(self):
        """Test network timeout handling - error callback should receive 'timeout' string"""
        runtime = LuaAsyncRuntime()
        runtime.initialize_lua()
        
        script = """
        timeout_occurred = false  -- Global variable
        error_status = nil  -- Global variable to capture the error status
        
        local client = net.HTTPClient()
        client:request("http://10.255.255.1:12345/timeout", {
            options = { 
                method = "GET",
                timeout = 1  -- 1 second timeout
            },
            success = function(response)
                -- Should not reach here
            end,
            error = function(status)
                timeout_occurred = true
                error_status = status  -- Capture the status passed to error callback
            end
        })
        """
        
        runtime.interpreter.lua.execute(script)
        
        # Wait for timeout
        await asyncio.sleep(3.0)
        
        timeout_occurred = runtime.interpreter.lua.eval("timeout_occurred")
        error_status = runtime.interpreter.lua.eval("error_status")
        
        assert timeout_occurred == True
        assert error_status == "timeout", f"Expected error status to be 'timeout', but got: {error_status}"
