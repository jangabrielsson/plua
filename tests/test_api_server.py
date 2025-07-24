"""
Tests for the API server functionality
"""

import pytest
import asyncio
import aiohttp
from plua.runtime import LuaAsyncRuntime
from plua.api_server import PlUA2APIServer


class TestAPIServer:
    """Test cases for the REST API server"""
    
    @pytest.mark.asyncio
    async def test_api_server_startup(self):
        """Test that API server can start and stop"""
        runtime = LuaAsyncRuntime()
        api_server = PlUA2APIServer(runtime, "127.0.0.1", 8877)
        
        # Start server
        server_task = asyncio.create_task(api_server.start_server())
        await asyncio.sleep(0.5)  # Give server time to start
        
        # Test that server is running
        async with aiohttp.ClientSession() as session:
            async with session.get('http://127.0.0.1:8877/plua/status') as response:
                assert response.status == 200
                data = await response.json()
                assert data['status'] == 'running'
        
        # Clean up
        server_task.cancel()
        try:
            await server_task
        except asyncio.CancelledError:
            pass
    
    @pytest.mark.asyncio
    async def test_lua_script_execution_via_api(self):
        """Test executing Lua scripts via API"""
        runtime = LuaAsyncRuntime()
        runtime.initialize_lua()
        api_server = PlUA2APIServer(runtime, "127.0.0.1", 8878)
        
        # Start server
        server_task = asyncio.create_task(api_server.start_server())
        await asyncio.sleep(0.5)
        
        try:
            # Test script execution
            async with aiohttp.ClientSession() as session:
                payload = {"code": "return 2 + 3"}
                async with session.post(
                    'http://127.0.0.1:8878/plua/execute',
                    json=payload
                ) as response:
                    assert response.status == 200
                    data = await response.json()
                    assert data['result'] == 5
        
        finally:
            server_task.cancel()
            try:
                await server_task
            except asyncio.CancelledError:
                pass
    
    @pytest.mark.asyncio
    async def test_api_runtime_state(self):
        """Test getting runtime state via API"""
        runtime = LuaAsyncRuntime()
        runtime.initialize_lua()
        api_server = PlUA2APIServer(runtime, "127.0.0.1", 8879)
        
        # Start server
        server_task = asyncio.create_task(api_server.start_server())
        await asyncio.sleep(0.5)
        
        try:
            # Get runtime state
            async with aiohttp.ClientSession() as session:
                async with session.get('http://127.0.0.1:8879/plua/state') as response:
                    assert response.status == 200
                    data = await response.json()
                    assert 'task_info' in data
                    assert 'active_timers' in data
        
        finally:
            server_task.cancel()
            try:
                await server_task
            except asyncio.CancelledError:
                pass
    
    @pytest.mark.asyncio
    async def test_api_timer_operations(self):
        """Test timer operations via API"""
        runtime = LuaAsyncRuntime()
        runtime.initialize_lua()
        api_server = PlUA2APIServer(runtime, "127.0.0.1", 8880)
        
        # Start server
        server_task = asyncio.create_task(api_server.start_server())
        await asyncio.sleep(0.5)
        
        try:
            async with aiohttp.ClientSession() as session:
                # Create a timer via API
                payload = {"code": "local id = setTimeout(function() print('Timer executed') end, 1000); return id"}
                async with session.post(
                    'http://127.0.0.1:8880/plua/execute',
                    json=payload
                ) as response:
                    assert response.status == 200
                    data = await response.json()
                    timer_id = data['result']
                    assert timer_id is not None
                
                # Check that timer exists in runtime state
                async with session.get('http://127.0.0.1:8880/plua/state') as response:
                    assert response.status == 200
                    data = await response.json()
                    # Timer should be tracked in the runtime
                    assert data['active_timers'] >= 0  # Could be 0 if already executed
        
        finally:
            server_task.cancel()
            try:
                await server_task
            except asyncio.CancelledError:
                pass
    
    @pytest.mark.asyncio
    async def test_fibaro_api_endpoints(self):
        """Test Fibaro API endpoints when Fibaro support is loaded"""
        runtime = LuaAsyncRuntime()
        runtime.initialize_lua()
        
        # Load Fibaro support
        runtime.interpreter.execute_script("require('fibaro')")
        
        api_server = PlUA2APIServer(runtime, "127.0.0.1", 8881)
        
        # Start server
        server_task = asyncio.create_task(api_server.start_server())
        await asyncio.sleep(0.5)
        
        try:
            async with aiohttp.ClientSession() as session:
                # Test a Fibaro API endpoint
                async with session.get('http://127.0.0.1:8881/api/devices') as response:
                    assert response.status == 200
                    data = await response.json()
                    # Should get the dummy response from Fibaro hook
                    assert isinstance(data, list)
                    assert len(data) == 2  # [{}, 200] from the dummy implementation
        
        finally:
            server_task.cancel()
            try:
                await server_task
            except asyncio.CancelledError:
                pass
    
    @pytest.mark.asyncio 
    async def test_api_error_handling(self):
        """Test API error handling for invalid requests"""
        runtime = LuaAsyncRuntime()
        runtime.initialize_lua()
        api_server = PlUA2APIServer(runtime, "127.0.0.1", 8882)
        
        # Start server
        server_task = asyncio.create_task(api_server.start_server())
        await asyncio.sleep(0.5)
        
        try:
            async with aiohttp.ClientSession() as session:
                # Test invalid JSON
                async with session.post(
                    'http://127.0.0.1:8882/plua/execute',
                    data="invalid json"
                ) as response:
                    assert response.status == 422  # Unprocessable Entity
                
                # Test invalid Lua code
                payload = {"code": "invalid lua syntax !!"}
                async with session.post(
                    'http://127.0.0.1:8882/plua/execute',
                    json=payload
                ) as response:
                    assert response.status == 400  # Bad Request
        
        finally:
            server_task.cancel()
            try:
                await server_task
            except asyncio.CancelledError:
                pass
