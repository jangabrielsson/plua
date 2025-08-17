"""
HTTP functionality for EPLua.

This module provides HTTP request capabilities that can be called from Lua scripts.
It also provides HTTP server functionality for testing and development.
For other network protocols, see separate modules: tcp.py, udp.py, websocket.py, mqtt.py
"""

import logging
import asyncio
import json
import requests  # For synchronous requests
from typing import Any, Dict, Optional
import aiohttp
from aiohttp import web
import uuid
from plua.lua_bindings import export_to_lua, get_global_engine, python_to_lua_table, lua_to_python_table

logger = logging.getLogger(__name__)


@export_to_lua("call_http")
def call_http(url: str, options: Any, callback_id: int) -> None:
    """
    Make an HTTP request with the given URL and options.
    
    Args:
        url: The URL to request
        options: Lua table with request options (method, headers, data, etc.)
        callback_id: ID of the registered Lua callback
    """
    # Convert Lua table to Python dict
    py_options = lua_to_python_table(options) if hasattr(options, 'items') else {}
    
    method = py_options.get('method', 'GET').upper()
    headers = py_options.get('headers', {})
    data = py_options.get('data')
    
    # Create options dict for the async function
    request_options = {
        'method': method,
        'headers': headers
    }
    
    if data is not None:
        request_options['data'] = data
    
    # Schedule the async request
    engine = get_global_engine()
    if engine and engine._timer_manager:
        asyncio.create_task(_perform_http_request(url, request_options, callback_id))


async def _perform_http_request(url: str, options: Dict[str, Any], callback_id: int) -> None:
    """
    Perform the actual HTTP request asynchronously.
    
    Args:
        url: The URL to request
        options: Request options (method, headers, data, etc.)
        callback_id: ID for the callback when request completes
    """
    engine = get_global_engine()
    if not engine:
        logger.error("No global engine available for HTTP callback")
        return
    
    try:
        # Extract options
        method = options.get('method', 'GET').upper()
        headers = options.get('headers', {})
        data = options.get('data')
        json_data = options.get('json')
        timeout = options.get('timeout', 30)
        
        # Prepare request kwargs
        request_kwargs = {
            'headers': headers,
            'timeout': aiohttp.ClientTimeout(total=timeout)
        }
        
        # Handle request body
        if json_data:
            request_kwargs['json'] = json_data
        elif data:
            request_kwargs['data'] = data
        
        # Make the HTTP request
        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, **request_kwargs) as response:
                # Get response text
                response_text = await response.text()
                
                # Try to parse as JSON
                try:
                    response_json = json.loads(response_text)
                except json.JSONDecodeError:
                    response_json = None
                
                # Prepare result
                result = {
                    'status': response.status,
                    'status_text': response.reason or '',
                    'headers': dict(response.headers),
                    'text': response_text,
                    'json': response_json,
                    'url': str(response.url),
                    'ok': 200 <= response.status < 300
                }
                
                logger.debug(f"HTTP request completed: {response.status} for {url}")
                
                # Call back to Lua with the result
                try:
                    # Convert response to Lua table
                    lua_result = python_to_lua_table(result)
                    engine._lua.globals()["_PY"]["timerExpired"](callback_id, None, lua_result)
                except Exception as e:
                    logger.error(f"Error calling HTTP callback {callback_id}: {e}")
                    
    except asyncio.TimeoutError:
        # logger.error(f"HTTP request timeout for {url}")
        error_message = f'Request to {url} timed out after {timeout} seconds'
        try:
            engine._lua.globals()["_PY"]["timerExpired"](callback_id, error_message, None)
        except Exception as e:
            logger.error(f"Error calling HTTP timeout callback {callback_id}: {e}")
            
    except Exception as e:
        # logger.error(f"HTTP request error for {url}: {e}")
        try:
            engine._lua.globals()["_PY"]["timerExpired"](callback_id, str(e), None)
        except Exception as e:
            logger.error(f"Error calling HTTP error callback {callback_id}: {e}")


@export_to_lua("http_request_sync")
def http_request_sync(options: Any) -> Any:
    """
    Make a synchronous HTTP request.
    
    Args:
        options: Lua table with request options (url, method, headers, data, etc.)
        
    Returns:
        Response table with status, body, headers, etc.
    """
    try:
        # Convert Lua table to Python dict
        py_options = lua_to_python_table(options) if hasattr(options, 'items') else {}
        
        url = py_options.get('url')
        if not url:
            return python_to_lua_table({'error': 'URL is required'})
            
        method = py_options.get('method', 'GET').upper()
        headers = py_options.get('headers', {})
        data = py_options.get('data')
        timeout = py_options.get('timeout', 30)
        
        # Make the synchronous request
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            data=data,
            timeout=timeout
        )
        
        # Try to parse JSON response
        response_json = None
        try:
            response_json = response.json()
        except Exception:
            pass
        
        # Create result
        result = {
            'status': response.status_code,
            'status_text': response.reason or '',
            'headers': dict(response.headers),
            'text': response.text,
            'json': response_json,
            'url': response.url,
            'ok': 200 <= response.status_code < 300
        }
        
        logger.debug(f"Sync HTTP request completed: {response.status_code} for {url}")
        return python_to_lua_table(result)
        
    except requests.RequestException as e:
        return python_to_lua_table({'error': str(e)})
    except Exception as e:
        return python_to_lua_table({'error': str(e)})


# ============================================================================
# HTTP Server Implementation
# ============================================================================

# Global registry for HTTP servers
_http_servers = {}

class HTTPServerHandler:
    """Handler for HTTP server instances"""
    
    def __init__(self, server_id: str):
        self.server_id = server_id
        self.app = None
        self.runner = None
        self.site = None
        self.callback_id = None
        self.pending_responses = {}  # Store pending response objects by request_id
        
    async def handle_request(self, request):
        """Handle incoming HTTP requests"""
        engine = get_global_engine()
        if not engine or not self.callback_id:
            return web.Response(text='{"error": "Server not properly configured"}', 
                              status=500, content_type='application/json')
        
        try:
            # Generate unique request ID for this request
            request_id = str(uuid.uuid4())
            
            # Read request body
            body = None
            if request.method in ['POST', 'PUT', 'PATCH']:
                try:
                    body = await request.text()
                except Exception as e:
                    logger.warning(f"Could not read request body: {e}")
                    body = ""
            
            # Store the response future so we can respond later
            response_future = asyncio.Future()
            self.pending_responses[request_id] = response_future
            
            # Prepare request data for Lua callback
            request_data = {
                'request_id': request_id,
                'method': request.method,
                'path': request.path_qs,  # Include query string
                'body': body or "",
                'headers': dict(request.headers)
            }
            
            # Call the Lua callback
            lua_request_data = python_to_lua_table(request_data)
            engine._lua.globals()["_PY"]["timerExpired"](self.callback_id, lua_request_data)
            
            # Wait for response from Lua (via http_server_respond)
            try:
                response_data = await asyncio.wait_for(response_future, timeout=30.0)
                
                # Prepare response headers
                response_headers = response_data.get('headers', {})
                if response_data.get('content_type'):
                    response_headers['Content-Type'] = response_data['content_type']
                
                return web.Response(
                    text=response_data['data'],
                    status=response_data['status_code'],
                    headers=response_headers
                )
            except asyncio.TimeoutError:
                # Clean up pending response
                self.pending_responses.pop(request_id, None)
                return web.Response(text='{"error": "Request timeout"}', 
                                  status=504, content_type='application/json')
                                  
        except Exception as e:
            logger.error(f"Error handling HTTP request: {e}")
            return web.Response(text=f'{{"error": "Internal server error: {e}"}}', 
                              status=500, content_type='application/json')
    
    def respond_to_request(self, request_id: str, data: str, status_code: int, content_type: str, headers: Dict[str, str] = None):
        """Respond to a pending HTTP request"""
        future = self.pending_responses.pop(request_id, None)
        if future and not future.done():
            future.set_result({
                'data': data,
                'status_code': status_code,
                'content_type': content_type,
                'headers': headers or {}
            })
            return True
        return False


@export_to_lua("http_server_create")
def http_server_create() -> str:
    """
    Create a new HTTP server instance.
    
    Returns:
        Server ID string that can be used with other server functions
    """
    server_id = str(uuid.uuid4())
    server_handler = HTTPServerHandler(server_id)
    _http_servers[server_id] = server_handler
    
    logger.debug(f"Created HTTP server with ID: {server_id}")
    return server_id


@export_to_lua("http_server_start")
def http_server_start(server_id: str, host: str, port: int, callback_id: int) -> None:
    """
    Start an HTTP server.
    
    Args:
        server_id: The server ID returned from http_server_create
        host: Host to bind to (e.g., "localhost", "0.0.0.0")
        port: Port to bind to
        callback_id: Lua callback ID for handling requests
    """
    server_handler = _http_servers.get(server_id)
    if not server_handler:
        logger.error(f"HTTP server {server_id} not found")
        return
    
    # Store callback ID for request handling
    server_handler.callback_id = callback_id
    
    # Schedule the server start
    asyncio.create_task(_start_http_server(server_handler, host, port))


async def _start_http_server(server_handler: HTTPServerHandler, host: str, port: int) -> None:
    """
    Actually start the HTTP server asynchronously.
    
    Args:
        server_handler: The server handler instance
        host: Host to bind to
        port: Port to bind to
    """
    try:
        # Create aiohttp application
        app = web.Application()
        server_handler.app = app
        
        # Add catch-all route handler
        app.router.add_route('*', '/{path:.*}', server_handler.handle_request)
        
        # Create runner and start server
        runner = web.AppRunner(app)
        server_handler.runner = runner
        await runner.setup()
        
        site = web.TCPSite(runner, host, port)
        server_handler.site = site
        await site.start()
        
        logger.info(f"HTTP server {server_handler.server_id} started on {host}:{port}")
        
    except Exception as e:
        logger.error(f"Error starting HTTP server {server_handler.server_id}: {e}")


@export_to_lua("http_server_respond")
def http_server_respond(*args) -> bool:
    """
    Respond to an HTTP request.
    
    Args can be:
        request_id, data, status_code, content_type, headers
        or
        request_id, data, status_code, content_type
        or 
        request_id, data, status_code
        
    Returns:
        True if response was sent successfully, False otherwise
    """
    # Parse arguments based on count
    if len(args) < 3:
        logger.error("http_server_respond requires at least 3 arguments")
        return False
        
    request_id = args[0]
    data = args[1]
    status_code = args[2]
    content_type = args[3] if len(args) > 3 else "application/json"
    headers = args[4] if len(args) > 4 else None
    
    # Convert Lua headers table to Python dict if provided
    response_headers = {}
    if headers:
        try:
            response_headers = lua_to_python_table(headers) if hasattr(headers, 'items') else headers
        except Exception as e:
            logger.warning(f"Failed to convert response headers: {e}")
            response_headers = {}
    
    # Find which server has this request
    for server_handler in _http_servers.values():
        if server_handler.respond_to_request(request_id, data, status_code, content_type, response_headers):
            logger.debug(f"Responded to request {request_id} with status {status_code}")
            return True
    
    logger.warning(f"Could not find pending request {request_id} to respond to")
    return False


@export_to_lua("http_server_stop")
def http_server_stop(server_id: str, callback_id: Optional[int] = None) -> None:
    """
    Stop an HTTP server.
    
    Args:
        server_id: The server ID to stop
        callback_id: Optional callback ID to call when stopped
    """
    server_handler = _http_servers.get(server_id)
    if not server_handler:
        logger.error(f"HTTP server {server_id} not found")
        if callback_id:
            engine = get_global_engine()
            if engine:
                try:
                    result = python_to_lua_table({'success': False, 'message': 'Server not found'})
                    engine._lua.globals()["_PY"]["timerExpired"](callback_id, result)
                except Exception as e:
                    logger.error(f"Error calling stop callback: {e}")
        return
    
    # Schedule the server stop
    asyncio.create_task(_stop_http_server(server_handler, callback_id))


async def _stop_http_server(server_handler: HTTPServerHandler, callback_id: Optional[int] = None) -> None:
    """
    Actually stop the HTTP server asynchronously.
    
    Args:
        server_handler: The server handler instance
        callback_id: Optional callback ID to call when stopped
    """
    try:
        # Clean up any pending responses
        for request_id, future in server_handler.pending_responses.items():
            if not future.done():
                future.set_result({
                    'data': '{"error": "Server shutting down"}',
                    'status_code': 503,
                    'content_type': 'application/json',
                    'headers': {}
                })
        server_handler.pending_responses.clear()
        
        # Stop the server
        if server_handler.site:
            await server_handler.site.stop()
            server_handler.site = None
            
        if server_handler.runner:
            await server_handler.runner.cleanup()
            server_handler.runner = None
            
        server_handler.app = None
        server_handler.callback_id = None
        
        # Remove from registry
        _http_servers.pop(server_handler.server_id, None)
        
        logger.info(f"HTTP server {server_handler.server_id} stopped successfully")
        
        # Call callback if provided
        if callback_id:
            engine = get_global_engine()
            if engine:
                try:
                    result = python_to_lua_table({'success': True, 'message': 'Server stopped successfully'})
                    engine._lua.globals()["_PY"]["timerExpired"](callback_id, result)
                except Exception as e:
                    logger.error(f"Error calling stop callback: {e}")
                    
    except Exception as e:
        logger.error(f"Error stopping HTTP server {server_handler.server_id}: {e}")
        
        # Call callback with error if provided
        if callback_id:
            engine = get_global_engine()
            if engine:
                try:
                    result = python_to_lua_table({'success': False, 'message': str(e)})
                    engine._lua.globals()["_PY"]["timerExpired"](callback_id, result)
                except Exception as e:
                    logger.error(f"Error calling stop callback: {e}")


@export_to_lua("http_server_is_running")
def http_server_is_running(server_id: str) -> bool:
    """
    Check if an HTTP server is currently running.
    
    Args:
        server_id: The server ID to check
        
    Returns:
        True if the server is running, False otherwise
    """
    server_handler = _http_servers.get(server_id)
    return server_handler is not None and server_handler.site is not None
