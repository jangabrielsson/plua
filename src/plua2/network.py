"""
Network functionality for plua2
Provides async HTTP, TCP, UDP and other network functions using the timer callback mechanism
"""

import asyncio
import aiohttp
from typing import Dict, Any, Optional
from .luafuns_lib import lua_exporter


# Global reference to the runtime (will be set when runtime starts)
_current_runtime: Optional[Any] = None


def set_current_runtime(runtime):
    """Set the current runtime reference for HTTP callbacks"""
    global _current_runtime
    _current_runtime = runtime


@lua_exporter.export(description="Make async HTTP request", category="http")
def http_request_async(request_table: Dict[str, Any], callback_id: int) -> None:
    """
    Make an async HTTP request and queue callback for execution
    
    Args:
        request_table: Dict with url, method, headers, body
        callback_id: Callback ID to execute when request completes
    """
    
    async def do_request():
        try:
            # Access Lua table fields directly
            url = request_table['url'] if 'url' in request_table else ''
            method = (request_table['method'] if 'method' in request_table else 'GET').upper()
            headers = dict(request_table['headers']) if 'headers' in request_table else {}
            body = request_table['body'] if 'body' in request_table else None
            timeout = request_table['timeout'] if 'timeout' in request_table else 30
            
            # Create timeout configuration
            timeout_config = aiohttp.ClientTimeout(total=timeout)
            
            async with aiohttp.ClientSession(timeout=timeout_config) as session:
                async with session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    data=body
                ) as response:
                    response_body = await response.text()
                    
                    # Create success response
                    result = {
                        'code': response.status,
                        'body': response_body,
                        'headers': dict(response.headers),
                        'error': None
                    }
                    
                    # Queue the callback for execution in the main loop
                    if _current_runtime:
                        _current_runtime.queue_lua_callback(callback_id, result)
                    
        except asyncio.TimeoutError:
            # Handle timeout
            error_result = {
                'error': 'Timeout',
                'code': 0,
                'body': None
            }
            if _current_runtime:
                _current_runtime.queue_lua_callback(callback_id, error_result)
                
        except Exception as e:
            # Handle other errors
            error_result = {
                'error': str(e),
                'code': 0,
                'body': None
            }
            if _current_runtime:
                _current_runtime.queue_lua_callback(callback_id, error_result)
    
    # Start the async work but don't wait for it
    asyncio.create_task(do_request())


# TCP socket connection management
_tcp_connections: Dict[int, tuple] = {}  # Store (reader, writer) tuples
_tcp_connection_counter = 0


@lua_exporter.export(description="Connect to TCP server", category="tcp")
def tcp_connect(host: str, port: int, callback_id: int) -> None:
    """
    Connect to a TCP server asynchronously
    
    Args:
        host: Server hostname or IP
        port: Server port
        callback_id: Callback ID to execute when connection completes
    """
    
    async def do_connect():
        global _tcp_connection_counter
        try:
            reader, writer = await asyncio.open_connection(host, port)
            
            # Store both reader and writer with unique ID
            _tcp_connection_counter += 1
            conn_id = _tcp_connection_counter
            _tcp_connections[conn_id] = (reader, writer)
            
            # Success result
            result = {
                'success': True,
                'conn_id': conn_id,
                'message': f'Connected to {host}:{port}'
            }
            
            if _current_runtime:
                _current_runtime.queue_lua_callback(callback_id, result)
                
        except Exception as e:
            # Error result
            result = {
                'success': False,
                'conn_id': None,
                'message': str(e)
            }
            
            if _current_runtime:
                _current_runtime.queue_lua_callback(callback_id, result)
    
    asyncio.create_task(do_connect())


@lua_exporter.export(description="Read data from TCP connection", category="tcp")
def tcp_read(conn_id: int, max_bytes: int, callback_id: int) -> None:
    """
    Read data from TCP connection asynchronously
    
    Args:
        conn_id: Connection ID
        max_bytes: Maximum bytes to read
        callback_id: Callback ID to execute when read completes
    """
    
    async def do_read():
        try:
            if conn_id not in _tcp_connections:
                result = {
                    'success': False,
                    'data': None,
                    'message': 'Connection not found'
                }
                if _current_runtime:
                    _current_runtime.queue_lua_callback(callback_id, result)
                return
            
            reader, writer = _tcp_connections[conn_id]
            
            # Read data using the reader
            data = await reader.read(max_bytes)
            
            result = {
                'success': True,
                'data': data.decode('utf-8', errors='replace'),
                'message': None
            }
            
            if _current_runtime:
                _current_runtime.queue_lua_callback(callback_id, result)
                
        except Exception as e:
            result = {
                'success': False,
                'data': None,
                'message': str(e)
            }
            
            if _current_runtime:
                _current_runtime.queue_lua_callback(callback_id, result)
    
    asyncio.create_task(do_read())


@lua_exporter.export(description="Read data from TCP connection until delimiter", category="tcp")
def tcp_read_until(conn_id: int, delimiter: str, max_bytes: int, callback_id: int) -> None:
    """
    Read data from TCP connection until delimiter is found
    
    Args:
        conn_id: Connection ID
        delimiter: Delimiter to read until
        max_bytes: Maximum bytes to read
        callback_id: Callback ID to execute when read completes
    """
    
    async def do_read_until():
        try:
            if conn_id not in _tcp_connections:
                result = {
                    'success': False,
                    'data': None,
                    'message': 'Connection not found'
                }
                if _current_runtime:
                    _current_runtime.queue_lua_callback(callback_id, result)
                return
            
            reader, writer = _tcp_connections[conn_id]
            
            # Simple implementation - read until delimiter
            buffer = b''
            delimiter_bytes = delimiter.encode('utf-8')
            
            while len(buffer) < max_bytes:
                chunk = await reader.read(1)
                if not chunk:
                    break
                buffer += chunk
                if delimiter_bytes in buffer:
                    break
            
            result = {
                'success': True,
                'data': buffer.decode('utf-8', errors='replace'),
                'message': None
            }
            
            if _current_runtime:
                _current_runtime.queue_lua_callback(callback_id, result)
                
        except Exception as e:
            result = {
                'success': False,
                'data': None,
                'message': str(e)
            }
            
            if _current_runtime:
                _current_runtime.queue_lua_callback(callback_id, result)
    
    asyncio.create_task(do_read_until())


@lua_exporter.export(description="Write data to TCP connection", category="tcp")
def tcp_write(conn_id: int, data: str, callback_id: int) -> None:
    """
    Write data to TCP connection asynchronously
    
    Args:
        conn_id: Connection ID
        data: Data to write
        callback_id: Callback ID to execute when write completes
    """
    
    async def do_write():
        try:
            if conn_id not in _tcp_connections:
                result = {
                    'success': False,
                    'bytes_written': 0,
                    'message': 'Connection not found'
                }
                if _current_runtime:
                    _current_runtime.queue_lua_callback(callback_id, result)
                return
            
            reader, writer = _tcp_connections[conn_id]
            data_bytes = data.encode('utf-8')
            writer.write(data_bytes)
            await writer.drain()
            
            result = {
                'success': True,
                'bytes_written': len(data_bytes),
                'message': None
            }
            
            if _current_runtime:
                _current_runtime.queue_lua_callback(callback_id, result)
                
        except Exception as e:
            result = {
                'success': False,
                'bytes_written': 0,
                'message': str(e)
            }
            
            if _current_runtime:
                _current_runtime.queue_lua_callback(callback_id, result)
    
    asyncio.create_task(do_write())


@lua_exporter.export(description="Close TCP connection", category="tcp")
def tcp_close(conn_id: int, callback_id: int) -> None:
    """
    Close TCP connection asynchronously
    
    Args:
        conn_id: Connection ID
        callback_id: Callback ID to execute when close completes
    """
    
    async def do_close():
        try:
            if conn_id not in _tcp_connections:
                result = {
                    'success': False,
                    'message': 'Connection not found'
                }
                if _current_runtime:
                    _current_runtime.queue_lua_callback(callback_id, result)
                return
            
            reader, writer = _tcp_connections[conn_id]
            writer.close()
            await writer.wait_closed()
            del _tcp_connections[conn_id]
            
            result = {
                'success': True,
                'message': 'Connection closed'
            }
            
            if _current_runtime:
                _current_runtime.queue_lua_callback(callback_id, result)
                
        except Exception as e:
            result = {
                'success': False,
                'message': str(e)
            }
            
            if _current_runtime:
                _current_runtime.queue_lua_callback(callback_id, result)
    
    asyncio.create_task(do_close())


# UDP socket management
_udp_sockets: Dict[int, asyncio.DatagramTransport] = {}
_udp_socket_counter = 0


@lua_exporter.export(description="Create UDP socket", category="udp")
def udp_create_socket(callback_id: int) -> None:
    """
    Create a UDP socket asynchronously
    
    Args:
        callback_id: Callback ID to execute when socket creation completes
    """
    
    async def do_create():
        global _udp_socket_counter
        try:
            # Create UDP socket
            transport, protocol = await asyncio.get_event_loop().create_datagram_endpoint(
                lambda: asyncio.DatagramProtocol(),
                local_addr=('0.0.0.0', 0)
            )
            
            _udp_socket_counter += 1
            socket_id = _udp_socket_counter
            _udp_sockets[socket_id] = transport
            
            result = {
                'success': True,
                'socket_id': socket_id,
                'message': 'UDP socket created'
            }
            
            if _current_runtime:
                _current_runtime.queue_lua_callback(callback_id, result)
                
        except Exception as e:
            result = {
                'success': False,
                'socket_id': None,
                'message': str(e)
            }
            
            if _current_runtime:
                _current_runtime.queue_lua_callback(callback_id, result)
    
    asyncio.create_task(do_create())


@lua_exporter.export(description="Send UDP data", category="udp")
def udp_send_to(socket_id: int, data: str, host: str, port: int, callback_id: int) -> None:
    """
    Send data via UDP socket asynchronously
    
    Args:
        socket_id: Socket ID
        data: Data to send
        host: Target hostname or IP
        port: Target port
        callback_id: Callback ID to execute when send completes
    """
    
    async def do_send():
        try:
            if socket_id not in _udp_sockets:
                result = {
                    'error': 'Socket not found'
                }
                if _current_runtime:
                    _current_runtime.queue_lua_callback(callback_id, result)
                return
            
            transport = _udp_sockets[socket_id]
            data_bytes = data.encode('utf-8')
            transport.sendto(data_bytes, (host, port))
            
            result = {
                'error': None
            }
            
            if _current_runtime:
                _current_runtime.queue_lua_callback(callback_id, result)
                
        except Exception as e:
            result = {
                'error': str(e)
            }
            
            if _current_runtime:
                _current_runtime.queue_lua_callback(callback_id, result)
    
    asyncio.create_task(do_send())


@lua_exporter.export(description="Close UDP socket", category="udp")
def udp_close(socket_id: int) -> None:
    """
    Close UDP socket
    
    Args:
        socket_id: Socket ID
    """
    if socket_id in _udp_sockets:
        transport = _udp_sockets[socket_id]
        transport.close()
        del _udp_sockets[socket_id]


@lua_exporter.export(description="Receive UDP data", category="udp")
def udp_receive(socket_id: int, callback_id: int) -> None:
    """
    Receive data via UDP socket asynchronously
    
    Args:
        socket_id: Socket ID
        callback_id: Callback ID to execute when receive completes
    """
    
    async def do_receive():
        try:
            if socket_id not in _udp_sockets:
                result = {
                    'data': None,
                    'ip': None,
                    'port': None,
                    'error': 'Socket not found'
                }
                if _current_runtime:
                    _current_runtime.queue_lua_callback(callback_id, result)
                return
            
            # Note: This is a simplified implementation
            # A full implementation would need to set up proper protocol handling
            # For now, we'll return an error indicating this needs more work
            result = {
                'data': None,
                'ip': None,
                'port': None,
                'error': 'UDP receive not fully implemented yet'
            }
            
            if _current_runtime:
                _current_runtime.queue_lua_callback(callback_id, result)
                
        except Exception as e:
            result = {
                'data': None,
                'ip': None,
                'port': None,
                'error': str(e)
            }
            
            if _current_runtime:
                _current_runtime.queue_lua_callback(callback_id, result)
    
    asyncio.create_task(do_receive())


# TCP server management
_tcp_servers: Dict[int, asyncio.Server] = {}
_tcp_server_counter = 0


@lua_exporter.export(description="Create TCP server", category="tcp")
def tcp_server_create() -> int:
    """
    Create a TCP server instance
    
    Returns:
        Server ID for the created server
    """
    global _tcp_server_counter
    _tcp_server_counter += 1
    server_id = _tcp_server_counter
    # We don't create the actual server yet, just reserve an ID
    return server_id


@lua_exporter.export(description="Start TCP server", category="tcp")
def tcp_server_start(server_id: int, host: str, port: int, callback_id: int) -> None:
    """
    Start TCP server listening on host:port
    
    Args:
        server_id: Server ID
        host: Host to bind to
        port: Port to bind to
        callback_id: Callback ID to execute when clients connect
    """
    
    async def handle_client(reader, writer):
        """Handle individual client connections"""
        try:
            # Get client information
            peername = writer.get_extra_info('peername')
            client_ip = peername[0] if peername else 'unknown'
            client_port = peername[1] if peername else 0
            
            # Store the client connection like a regular TCP connection
            global _tcp_connection_counter
            _tcp_connection_counter += 1
            conn_id = _tcp_connection_counter
            _tcp_connections[conn_id] = (reader, writer)
            
            # Create result for the callback
            result = {
                'success': True,
                'conn_id': conn_id,
                'client_ip': client_ip,
                'client_port': client_port
            }
            
            if _current_runtime:
                _current_runtime.queue_lua_callback(callback_id, result)
                
        except Exception as e:
            # Handle client connection errors
            result = {
                'success': False,
                'conn_id': None,
                'client_ip': None,
                'client_port': None,
                'error': str(e)
            }
            
            if _current_runtime:
                _current_runtime.queue_lua_callback(callback_id, result)
    
    async def start_server():
        try:
            # Create and start the server
            server = await asyncio.start_server(handle_client, host, port)
            _tcp_servers[server_id] = server
            
            # Notify that server started successfully
            result = {
                'success': True,
                'message': f'TCP server started on {host}:{port}',
                'host': host,
                'port': port
            }
            
            if _current_runtime:
                # Use a different callback for server start notifications
                # For now, we'll just print this
                print(f"[TCP] Server {server_id} started on {host}:{port}")
                
        except Exception as e:
            result = {
                'success': False,
                'message': str(e),
                'host': host,
                'port': port
            }
            
            print(f"[TCP] Server {server_id} failed to start: {e}")
    
    asyncio.create_task(start_server())


@lua_exporter.export(description="Stop TCP server", category="tcp")
def tcp_server_stop(server_id: int, callback_id: int) -> None:
    """
    Stop TCP server
    
    Args:
        server_id: Server ID
        callback_id: Callback ID to execute when server stops
    """
    
    async def stop_server():
        try:
            if server_id in _tcp_servers:
                server = _tcp_servers[server_id]
                server.close()
                await server.wait_closed()
                del _tcp_servers[server_id]
                
                result = {
                    'success': True,
                    'message': 'TCP server stopped'
                }
            else:
                result = {
                    'success': False,
                    'message': 'Server not found'
                }
            
            if _current_runtime:
                _current_runtime.queue_lua_callback(callback_id, result)
                
        except Exception as e:
            result = {
                'success': False,
                'message': str(e)
            }
            
            if _current_runtime:
                _current_runtime.queue_lua_callback(callback_id, result)
    
    asyncio.create_task(stop_server())


# HTTP server management
_http_servers: Dict[int, asyncio.Server] = {}
_http_server_counter = 0
_http_response_writers: Dict[int, Any] = {}


async def send_http_response(writer, status_code: int, data: str, content_type: str = "text/plain"):
    """Send HTTP response to client"""
    try:
        # HTTP status line
        status_line = f"HTTP/1.1 {status_code} {get_status_text(status_code)}\r\n"
        
        # Headers
        headers = [
            f"Content-Type: {content_type}",
            f"Content-Length: {len(data.encode('utf-8'))}",
            "Connection: close",
            "Server: plua2-http/1.0"
        ]
        
        # Complete response
        response = status_line + '\r\n'.join(headers) + '\r\n\r\n' + data
        
        writer.write(response.encode('utf-8'))
        await writer.drain()
        writer.close()
        await writer.wait_closed()
        
    except Exception as e:
        print(f"[HTTP] Error sending response: {e}")
        import traceback
        traceback.print_exc()


def get_status_text(status_code: int) -> str:
    """Get HTTP status text for status code"""
    status_texts = {
        200: "OK",
        201: "Created",
        400: "Bad Request", 
        401: "Unauthorized",
        403: "Forbidden",
        404: "Not Found",
        405: "Method Not Allowed",
        500: "Internal Server Error",
        501: "Not Implemented",
        502: "Bad Gateway",
        503: "Service Unavailable"
    }
    return status_texts.get(status_code, "Unknown")


@lua_exporter.export(description="Create HTTP server", category="http")
def http_server_create() -> int:
    """
    Create an HTTP server instance
    
    Returns:
        Server ID for the created server
    """
    global _http_server_counter
    _http_server_counter += 1
    server_id = _http_server_counter
    # We don't create the actual server yet, just reserve an ID
    return server_id


@lua_exporter.export(description="Start HTTP server", category="http") 
def http_server_start(server_id: int, host: str, port: int, callback_id: int) -> None:
    """
    Start HTTP server listening on host:port
    
    Args:
        server_id: Server ID
        host: Host to bind to
        port: Port to bind to
        callback_id: Callback ID to execute when HTTP requests arrive
    """
    
    async def handle_request(reader, writer):
        """Handle individual HTTP requests"""
        try:
            # Read the HTTP request
            request_data = b""
            while True:
                line = await reader.readline()
                request_data += line
                if line == b'\r\n':  # End of headers
                    break
                if not line:  # Connection closed
                    break
            
            # Parse the request line and headers
            request_lines = request_data.decode('utf-8', errors='replace').split('\r\n')
            if not request_lines:
                writer.close()
                return
                
            # Parse request line (e.g., "GET /path HTTP/1.1")
            request_line = request_lines[0].split()
            if len(request_line) < 3:
                writer.close()
                return
                
            method = request_line[0]
            path = request_line[1]
            
            # Parse headers
            headers = {}
            content_length = 0
            for line in request_lines[1:]:
                if ':' in line:
                    key, value = line.split(':', 1)
                    headers[key.strip().lower()] = value.strip()
                    if key.strip().lower() == 'content-length':
                        content_length = int(value.strip())
            
            # Read body if present
            body = ""
            if content_length > 0:
                body_data = await reader.read(content_length)
                body = body_data.decode('utf-8', errors='replace')
            
            # Get client information
            peername = writer.get_extra_info('peername')
            client_ip = peername[0] if peername else 'unknown'
            client_port = peername[1] if peername else 0
            
            # Create request object for the callback
            request_obj = {
                'method': method,
                'path': path,
                'headers': headers,
                'body': body,
                'client_ip': client_ip,
                'client_port': client_port,
                'writer': writer  # We'll store the writer to respond later
            }
            
            # Store the writer for this request (simple approach for now)
            request_id = id(writer)  # Use writer object id as unique request id
            _http_response_writers[request_id] = writer
            request_obj['request_id'] = request_id
            
            # Queue the callback for Lua execution
            if _current_runtime:
                print(f"[HTTP] Queueing callback for {method} {path} with callback_id {callback_id}")
                print(f"[HTTP] Request object keys: {list(request_obj.keys())}")
                _current_runtime.queue_lua_callback(callback_id, request_obj)
                print(f"[HTTP] Callback queued successfully")
            else:
                print(f"[HTTP] No runtime available, sending fallback error")
                # Fallback if no runtime
                asyncio.create_task(send_http_response(writer, 500, "Internal Server Error", "text/plain"))
                
        except Exception as e:
            print(f"[HTTP] Error handling request: {e}")
            try:
                asyncio.create_task(send_http_response(writer, 500, f"Internal Server Error: {e}", "text/plain"))
            except:
                pass
    
    async def start_server():
        try:
            # Create and start the HTTP server
            # Convert "localhost" to explicit IPv4 address to avoid IPv6/IPv4 binding issues
            bind_host = "127.0.0.1" if host == "localhost" else host
            server = await asyncio.start_server(handle_request, bind_host, port)
            _http_servers[server_id] = server
            
            print(f"[HTTP] Server {server_id} started on {bind_host}:{port} (requested: {host}:{port})")
                
        except Exception as e:
            print(f"[HTTP] Server {server_id} failed to start: {e}")
            # Try binding to all interfaces as fallback
            try:
                print(f"[HTTP] Retrying server {server_id} on 0.0.0.0:{port}")
                server = await asyncio.start_server(handle_request, "0.0.0.0", port)
                _http_servers[server_id] = server
                print(f"[HTTP] Server {server_id} started on 0.0.0.0:{port} (fallback)")
            except Exception as e2:
                print(f"[HTTP] Server {server_id} fallback also failed: {e2}")
    
    asyncio.create_task(start_server())


@lua_exporter.export(description="Stop HTTP server", category="http")
def http_server_stop(server_id: int, callback_id: int) -> None:
    """
    Stop HTTP server
    
    Args:
        server_id: Server ID
        callback_id: Callback ID to execute when server stops
    """
    
    async def stop_server():
        try:
            if server_id in _http_servers:
                server = _http_servers[server_id]
                server.close()
                await server.wait_closed()
                del _http_servers[server_id]
                
                result = {
                    'success': True,
                    'message': 'HTTP server stopped'
                }
            else:
                result = {
                    'success': False,
                    'message': 'Server not found'
                }
            
            if _current_runtime:
                _current_runtime.queue_lua_callback(callback_id, result)
                
        except Exception as e:
            result = {
                'success': False,
                'message': str(e)
            }
            
            if _current_runtime:
                _current_runtime.queue_lua_callback(callback_id, result)
    
    asyncio.create_task(stop_server())


@lua_exporter.export(description="Send HTTP response", category="http")
def http_server_respond(request_id: int, data: str, status_code: int = 200, content_type: str = "application/json") -> None:
    """
    Send HTTP response back to client
    
    Args:
        request_id: The request ID from the request object
        data: Response data to send
        status_code: HTTP status code (default 200)
        content_type: Content type header (default application/json)
    """
    
    if request_id in _http_response_writers:
        writer = _http_response_writers[request_id]
        
        async def send_response():
            await send_http_response(writer, status_code, data, content_type)
            # Clean up
            if request_id in _http_response_writers:
                del _http_response_writers[request_id]
        
        asyncio.create_task(send_response())
    else:
        print(f"[HTTP] Warning: Request ID {request_id} not found for response")


# WebSocket connection management
_websocket_connections: Dict[int, Any] = {}  # Store WebSocket connections
_websocket_connection_counter = 0

# WebSocket server management
_websocket_servers: Dict[int, Any] = {}  # Store WebSocket servers
_websocket_server_counter = 0


@lua_exporter.export(description="Create WebSocket connection", category="websocket")
def websocket_connect(url: str, callback_id: int, headers: Optional[Dict[str, str]] = None) -> int:
    """
    Connect to a WebSocket server asynchronously
    
    Args:
        url: WebSocket URL (ws:// or wss://)
        callback_id: Callback ID for all WebSocket events
        headers: Optional headers for connection
        
    Returns:
        Connection ID for this WebSocket
    """
    import aiohttp
    import ssl
    
    global _websocket_connection_counter, _websocket_connections
    _websocket_connection_counter += 1
    conn_id = _websocket_connection_counter
    
    async def do_connect():
        try:
            headers_dict = headers or {}
            
            # Handle SSL context for wss:// URLs
            ssl_context = None
            if url.startswith('wss://'):
                ssl_context = ssl.create_default_context()
                # For development, you might want to disable certificate verification
                # ssl_context.check_hostname = False
                # ssl_context.verify_mode = ssl.CERT_NONE
            
            session = aiohttp.ClientSession()
            ws = await session.ws_connect(url, headers=headers_dict, ssl=ssl_context)
            
            # Store the connection
            _websocket_connections[conn_id] = {
                'ws': ws,
                'session': session,
                'url': url,
                'connected': True,
                'callback_id': callback_id
            }
            
            # Only log in debug mode
            if _current_runtime and hasattr(_current_runtime.interpreter, '_debug') and _current_runtime.interpreter._debug:
                print(f"[WebSocket {conn_id}] Connected successfully")
            
            # Notify connection success
            if _current_runtime:
                _current_runtime.queue_lua_callback(callback_id, {
                    'event': 'connected',
                    'conn_id': conn_id,
                    'success': True
                })
            
            # Start listening for messages
            async def listen_messages():
                try:
                    async for msg in ws:
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            if _current_runtime:
                                _current_runtime.queue_lua_callback(callback_id, {
                                    'event': 'dataReceived',
                                    'conn_id': conn_id,
                                    'data': msg.data
                                })
                        elif msg.type == aiohttp.WSMsgType.BINARY:
                            if _current_runtime:
                                _current_runtime.queue_lua_callback(callback_id, {
                                    'event': 'dataReceived',
                                    'conn_id': conn_id,
                                    'data': msg.data.decode('utf-8', errors='ignore')
                                })
                        elif msg.type == aiohttp.WSMsgType.ERROR:
                            if _current_runtime:
                                _current_runtime.queue_lua_callback(callback_id, {
                                    'event': 'error',
                                    'conn_id': conn_id,
                                    'error': f"WebSocket error: {ws.exception()}"
                                })
                            break
                        elif msg.type == aiohttp.WSMsgType.CLOSE:
                            break
                            
                except Exception as e:
                    print(f"[WebSocket {conn_id}] Exception in message loop: {e}")
                    if _current_runtime:
                        _current_runtime.queue_lua_callback(callback_id, {
                            'event': 'error',
                            'conn_id': conn_id,
                            'error': f"Message listening error: {str(e)}"
                        })
                finally:
                    # Connection closed - be careful about race conditions with close()
                    if conn_id in _websocket_connections:
                        try:
                            _websocket_connections[conn_id]['connected'] = False
                            await session.close()
                            
                            # Send disconnected event before cleanup
                            if _current_runtime:
                                _current_runtime.queue_lua_callback(callback_id, {
                                    'event': 'disconnected',
                                    'conn_id': conn_id
                                })
                        except Exception as e:
                            print(f"[WebSocket {conn_id}] Error during cleanup: {e}")
                        finally:
                            # Always remove from connections dict
                            if conn_id in _websocket_connections:
                                del _websocket_connections[conn_id]
            
            # Start the message listener
            asyncio.create_task(listen_messages())
            
        except Exception as e:
            # Handle connection errors
            if _current_runtime:
                _current_runtime.queue_lua_callback(callback_id, {
                    'event': 'error',
                    'conn_id': conn_id,
                    'error': f"Connection error: {str(e)}",
                    'success': False
                })
    
    # Start the async connection
    asyncio.create_task(do_connect())
    return conn_id


@lua_exporter.export(description="Send data through WebSocket", category="websocket")
def websocket_send(conn_id: int, data: str, callback_id: Optional[int] = None) -> None:
    """
    Send data through a WebSocket connection
    
    Args:
        conn_id: WebSocket connection ID
        data: Data to send (string)
        callback_id: Optional callback for send completion
    """
    
    async def do_send():
        try:
            if conn_id not in _websocket_connections:
                error_msg = f"WebSocket connection {conn_id} not found"
                if callback_id and _current_runtime:
                    _current_runtime.queue_lua_callback(callback_id, {
                        'success': False,
                        'error': error_msg
                    })
                return
            
            conn_info = _websocket_connections[conn_id]
            if not conn_info['connected']:
                error_msg = f"WebSocket connection {conn_id} is not connected"
                if callback_id and _current_runtime:
                    _current_runtime.queue_lua_callback(callback_id, {
                        'success': False,
                        'error': error_msg
                    })
                return
            
            ws = conn_info['ws']
            await ws.send_str(data)
            
            # Notify send success
            if callback_id and _current_runtime:
                _current_runtime.queue_lua_callback(callback_id, {
                    'success': True
                })
                
        except Exception as e:
            error_msg = f"WebSocket send error: {str(e)}"
            if callback_id and _current_runtime:
                _current_runtime.queue_lua_callback(callback_id, {
                    'success': False,
                    'error': error_msg
                })
    
    asyncio.create_task(do_send())


@lua_exporter.export(description="Close WebSocket connection", category="websocket")
def websocket_close(conn_id: int, callback_id: Optional[int] = None) -> None:
    """
    Close a WebSocket connection
    
    Args:
        conn_id: WebSocket connection ID
        callback_id: Optional callback for close completion
    """
    
    async def do_close():
        try:
            if conn_id not in _websocket_connections:
                error_msg = f"WebSocket connection {conn_id} not found"
                if callback_id and _current_runtime:
                    _current_runtime.queue_lua_callback(callback_id, {
                        'success': False,
                        'error': error_msg
                    })
                return
            
            conn_info = _websocket_connections[conn_id]
            ws = conn_info['ws']
            session = conn_info['session']
            
            # Close the WebSocket
            await ws.close()
            await session.close()
            
            # Mark as disconnected and remove from connections
            conn_info['connected'] = False
            if conn_id in _websocket_connections:
                del _websocket_connections[conn_id]
            
            # Notify close success
            if callback_id and _current_runtime:
                _current_runtime.queue_lua_callback(callback_id, {
                    'success': True
                })
                
        except Exception as e:
            error_msg = f"WebSocket close error: {str(e)}"
            if callback_id and _current_runtime:
                _current_runtime.queue_lua_callback(callback_id, {
                    'success': False,
                    'error': error_msg
                })
    
    asyncio.create_task(do_close())


@lua_exporter.export(description="Check if WebSocket is open", category="websocket")
def websocket_is_open(conn_id: int) -> bool:
    """
    Check if a WebSocket connection is open
    
    Args:
        conn_id: WebSocket connection ID
        
    Returns:
        True if connection is open, False otherwise
    """
    if conn_id not in _websocket_connections:
        return False
    
    conn_info = _websocket_connections[conn_id]
    return conn_info['connected'] and not conn_info['ws'].closed


# WebSocket Server Implementation

@lua_exporter.export(description="Create WebSocket server", category="websocket")
def websocket_server_create() -> int:
    """
    Create a new WebSocket server
    
    Returns:
        Server ID for this WebSocket server
    """
    global _websocket_server_counter
    _websocket_server_counter += 1
    server_id = _websocket_server_counter
    
    _websocket_servers[server_id] = {
        'server': None,
        'clients': {},  # client_id -> client_info
        'client_counter': 0,
        'running': False,
        'host': None,
        'port': None
    }
    
    return server_id


@lua_exporter.export(description="Start WebSocket server", category="websocket")
def websocket_server_start(server_id: int, host: str, port: int, callback_id: int) -> None:
    """
    Start a WebSocket server
    
    Args:
        server_id: WebSocket server ID
        host: Host to bind to
        port: Port to listen on
        callback_id: Callback ID for server events
    """
    import aiohttp
    from aiohttp import web
    
    if server_id not in _websocket_servers:
        if _current_runtime:
            _current_runtime.queue_lua_callback(callback_id, {
                'event': 'error',
                'error': f'Server {server_id} not found'
            })
        return
    
    server_info = _websocket_servers[server_id]
    
    async def websocket_handler(request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        # Create client ID and info
        server_info['client_counter'] += 1
        client_id = server_info['client_counter']
        
        client_info = {
            'id': client_id,
            'ws': ws,
            'request': request,
            'connected': True
        }
        
        server_info['clients'][client_id] = client_info
        
        # Notify client connected
        if _current_runtime:
            _current_runtime.queue_lua_callback(callback_id, {
                'event': 'connected',
                'server_id': server_id,
                'client_id': client_id
            })
        
        try:
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    # Notify message received
                    if _current_runtime:
                        _current_runtime.queue_lua_callback(callback_id, {
                            'event': 'receive',
                            'server_id': server_id,
                            'client_id': client_id,
                            'data': msg.data
                        })
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    # Notify error
                    if _current_runtime:
                        _current_runtime.queue_lua_callback(callback_id, {
                            'event': 'error',
                            'server_id': server_id,
                            'client_id': client_id,
                            'error': f'WebSocket error: {ws.exception()}'
                        })
                    break
                elif msg.type == aiohttp.WSMsgType.CLOSE:
                    break
        except Exception as e:
            if _current_runtime:
                _current_runtime.queue_lua_callback(callback_id, {
                    'event': 'error',
                    'server_id': server_id,
                    'client_id': client_id,
                    'error': f'Message handling error: {str(e)}'
                })
        finally:
            # Client disconnected
            if client_id in server_info['clients']:
                server_info['clients'][client_id]['connected'] = False
                del server_info['clients'][client_id]
            
            if _current_runtime:
                _current_runtime.queue_lua_callback(callback_id, {
                    'event': 'disconnected',
                    'server_id': server_id,
                    'client_id': client_id
                })
        
        return ws
    
    async def start_server():
        try:
            app = web.Application()
            app.router.add_get('/', websocket_handler)
            
            runner = web.AppRunner(app)
            await runner.setup()
            
            site = web.TCPSite(runner, host, port)
            await site.start()
            
            server_info['server'] = runner
            server_info['running'] = True
            server_info['host'] = host
            server_info['port'] = port
            
            # Notify server started
            if _current_runtime:
                _current_runtime.queue_lua_callback(callback_id, {
                    'event': 'started',
                    'server_id': server_id,
                    'host': host,
                    'port': port
                })
            
        except Exception as e:
            # Notify start error
            if _current_runtime:
                _current_runtime.queue_lua_callback(callback_id, {
                    'event': 'error',
                    'server_id': server_id,
                    'error': f'Failed to start server: {str(e)}'
                })
    
    asyncio.create_task(start_server())


@lua_exporter.export(description="Send data to WebSocket client", category="websocket")
def websocket_server_send(server_id: int, client_id: int, data: str, callback_id: Optional[int] = None) -> None:
    """
    Send data to a specific WebSocket client
    
    Args:
        server_id: WebSocket server ID
        client_id: Client ID to send to
        data: Data to send
        callback_id: Optional callback for send completion
    """
    
    async def do_send():
        try:
            if server_id not in _websocket_servers:
                error_msg = f"Server {server_id} not found"
                if callback_id and _current_runtime:
                    _current_runtime.queue_lua_callback(callback_id, {
                        'success': False,
                        'error': error_msg
                    })
                return
            
            server_info = _websocket_servers[server_id]
            
            if client_id not in server_info['clients']:
                error_msg = f"Client {client_id} not found"
                if callback_id and _current_runtime:
                    _current_runtime.queue_lua_callback(callback_id, {
                        'success': False,
                        'error': error_msg
                    })
                return
            
            client_info = server_info['clients'][client_id]
            if not client_info['connected']:
                error_msg = f"Client {client_id} not connected"
                if callback_id and _current_runtime:
                    _current_runtime.queue_lua_callback(callback_id, {
                        'success': False,
                        'error': error_msg
                    })
                return
            
            ws = client_info['ws']
            await ws.send_str(data)
            
            # Notify send success
            if callback_id and _current_runtime:
                _current_runtime.queue_lua_callback(callback_id, {
                    'success': True
                })
                
        except Exception as e:
            error_msg = f"Send error: {str(e)}"
            if callback_id and _current_runtime:
                _current_runtime.queue_lua_callback(callback_id, {
                    'success': False,
                    'error': error_msg
                })
    
    asyncio.create_task(do_send())


@lua_exporter.export(description="Stop WebSocket server", category="websocket")
def websocket_server_stop(server_id: int, callback_id: Optional[int] = None) -> None:
    """
    Stop a WebSocket server
    
    Args:
        server_id: WebSocket server ID
        callback_id: Optional callback for stop completion
    """
    
    async def do_stop():
        try:
            if server_id not in _websocket_servers:
                error_msg = f"Server {server_id} not found"
                if callback_id and _current_runtime:
                    _current_runtime.queue_lua_callback(callback_id, {
                        'success': False,
                        'error': error_msg
                    })
                return
            
            server_info = _websocket_servers[server_id]
            
            if server_info['server']:
                await server_info['server'].cleanup()
                server_info['server'] = None
            
            # Close all client connections
            for client_info in server_info['clients'].values():
                if client_info['connected']:
                    await client_info['ws'].close()
            
            server_info['clients'].clear()
            server_info['running'] = False
            
            # Notify stop success
            if callback_id and _current_runtime:
                _current_runtime.queue_lua_callback(callback_id, {
                    'success': True
                })
                
        except Exception as e:
            error_msg = f"Stop error: {str(e)}"
            if callback_id and _current_runtime:
                _current_runtime.queue_lua_callback(callback_id, {
                    'success': False,
                    'error': error_msg
                })
    
    asyncio.create_task(do_stop())


@lua_exporter.export(description="Check if WebSocket server is running", category="websocket")
def websocket_server_is_running(server_id: int) -> bool:
    """
    Check if a WebSocket server is running
    
    Args:
        server_id: WebSocket server ID
        
    Returns:
        True if server is running, False otherwise
    """
    if server_id not in _websocket_servers:
        return False
    
    return _websocket_servers[server_id]['running']


# ============================================================================
# MQTT Client Implementation
# ============================================================================

import paho.mqtt.client as mqtt_client
import uuid
import aiomqtt
from aiomqtt import Client as AioMQTTClient, MqttError


# Global storage for MQTT clients
_mqtt_clients: Dict[int, Dict[str, Any]] = {}
_mqtt_client_counter = 0


def _generate_mqtt_client_id() -> int:
    """Generate a unique MQTT client ID"""
    global _mqtt_client_counter
    _mqtt_client_counter += 1
    return _mqtt_client_counter


@lua_exporter.export(description="Connect to MQTT broker", category="mqtt")
def mqtt_client_connect(uri: str, options: Optional[Dict[str, Any]] = None, callback_id: Optional[int] = None) -> int:
    """
    Connect to MQTT broker following Fibaro HC3 specification
    
    Args:
        uri: Broker URI (mqtt://host:port or mqtts://host:port or just host)
        options: Connection options dict
        callback_id: Optional callback for connection result
        
    Returns:
        MQTT client ID
    """
    client_id = _generate_mqtt_client_id()
    opts = options or {}

    # Parse URI and determine connection details
    use_tls = False
    host = uri
    port = 1883
    if uri.startswith('mqtts://'):
        use_tls = True
        host = uri[8:]
        port = 8883
    elif uri.startswith('mqtt://'):
        host = uri[7:]
        port = 1883
    # Extract host and port if specified
    if ':' in host:
        host_parts = host.split(':')
        host = host_parts[0]
        port = int(host_parts[1])
    # Override port if specified in options
    if 'port' in opts:
        port = opts['port']
    # Generate client ID if not provided
    mqtt_client_id = opts['clientId'] if 'clientId' in opts else f"plua2_mqtt_{uuid.uuid4().hex[:8]}"
    keep_alive = opts['keepAlivePeriod'] if 'keepAlivePeriod' in opts else 60
    username = opts['username'] if 'username' in opts else None
    password = opts['password'] if 'password' in opts else None

    # Store client info
    client_info = {
        'client': None,  # Will be set after connect
        'connected': False,
        'events': {},  # Event listeners
        'subscriptions': {},  # Track subscriptions
        'client_id': mqtt_client_id,
        'host': host,
        'port': port,
        'use_tls': use_tls,
        'task': None
    }
    _mqtt_clients[client_id] = client_info

    async def mqtt_connect_task():
        print("[DEBUG] Inside mqtt_connect_task (aiomqtt)")
        try:
            print(f"[DEBUG] Connecting to MQTT broker at {host}:{port} as {mqtt_client_id}")
            async with AioMQTTClient(
                hostname=host,
                port=port,
                username=username,
                password=password,
                tls_context=None if not use_tls else None  # TODO: support custom TLS
            ) as client:
                await client.connect(
                    client_id=mqtt_client_id,
                    keepalive=keep_alive
                )
                print("[DEBUG] Connected to MQTT broker (aiomqtt)")
                client_info['client'] = client
                client_info['connected'] = True
                if _current_runtime and callback_id:
                    print("[DEBUG] Calling Lua callback for 'connected' event")
                    _current_runtime.queue_lua_callback(callback_id, {
                        'event': 'connected',
                        'client_id': client_id,
                        'success': True
                    })
                async for message in client.messages():
                    print("[DEBUG] Received message:", message)
                    if _current_runtime:
                        _current_runtime.queue_lua_callback(callback_id, {
                            'event': 'message',
                            'client_id': client_id,
                            'topic': message.topic,
                            'payload': message.payload.decode('utf-8', errors='replace')
                        })
        except MqttError as e:
            print("[DEBUG] MqttError in mqtt_connect_task:", e)
            client_info['connected'] = False
            if _current_runtime and callback_id:
                print("[DEBUG] Calling Lua callback for 'error' event (MqttError)")
                _current_runtime.queue_lua_callback(callback_id, {
                    'event': 'error',
                    'client_id': client_id,
                    'error': str(e),
                    'success': False
                })
        except Exception as e:
            print("[DEBUG] Exception in mqtt_connect_task:", e)
            client_info['connected'] = False
            if _current_runtime and callback_id:
                print("[DEBUG] Calling Lua callback for 'error' event (Exception)")
                _current_runtime.queue_lua_callback(callback_id, {
                    'event': 'error',
                    'client_id': client_id,
                    'error': str(e),
                    'success': False
                })

    print("[DEBUG] About to call asyncio.create_task with:", mqtt_connect_task)
    print("[DEBUG] asyncio.create_task is:", getattr(asyncio, 'create_task', None))
    # Start the async MQTT connect task
    task = asyncio.create_task(mqtt_connect_task())
    client_info['task'] = task
    return client_id


@lua_exporter.export(description="Disconnect MQTT client", category="mqtt")
def mqtt_client_disconnect(client_id: int, options: Optional[Dict[str, Any]] = None, callback_id: Optional[int] = None) -> None:
    """
    Disconnect MQTT client
    
    Args:
        client_id: MQTT client ID
        options: Disconnect options
        callback_id: Optional callback
    """
    if client_id not in _mqtt_clients:
        if callback_id and _current_runtime:
            _current_runtime.queue_lua_callback(callback_id, 1)  # Error
        return
    
    async def do_disconnect():
        try:
            client_info = _mqtt_clients[client_id]
            client = client_info['client']
            
            if client_info['connected']:
                client.disconnect()
                client.loop_stop()
                client_info['connected'] = False
            
            if callback_id and _current_runtime:
                _current_runtime.queue_lua_callback(callback_id, 0)  # Success
                
        except Exception as e:
            if callback_id and _current_runtime:
                _current_runtime.queue_lua_callback(callback_id, 1)  # Error
    
    asyncio.create_task(do_disconnect())


@lua_exporter.export(description="Subscribe to MQTT topic", category="mqtt")
def mqtt_client_subscribe(client_id: int, topics, options: Optional[Dict[str, Any]] = None, callback_id: Optional[int] = None) -> Optional[int]:
    """
    Subscribe to MQTT topic(s)
    
    Args:
        client_id: MQTT client ID
        topics: Topic string or list of topics
        options: Subscribe options
        callback_id: Optional callback
        
    Returns:
        Packet ID
    """
    if client_id not in _mqtt_clients:
        if callback_id and _current_runtime:
            _current_runtime.queue_lua_callback(callback_id, 1)  # Error
        return None
    
    client_info = _mqtt_clients[client_id]
    client = client_info['client']
    
    if not client_info['connected']:
        if callback_id and _current_runtime:
            _current_runtime.queue_lua_callback(callback_id, 1)  # Error
        return None
    
    if options is None:
        options = {}
    
    default_qos = options.get('qos', 0)
    
    try:
        # Handle single topic or multiple topics
        if isinstance(topics, str):
            # Single topic
            result, mid = client.subscribe(topics, default_qos)
        elif isinstance(topics, list):
            # Multiple topics
            topic_list = []
            for topic in topics:
                if isinstance(topic, str):
                    topic_list.append((topic, default_qos))
                elif isinstance(topic, dict) and 'topic' in topic:
                    qos = topic.get('qos', default_qos)
                    topic_list.append((topic['topic'], qos))
                elif isinstance(topic, list) and len(topic) >= 2:
                    # [topic, qos] format
                    topic_list.append((topic[0], topic[1]))
                else:
                    # Fallback: treat as string
                    topic_list.append((str(topic), default_qos))
            
            result, mid = client.subscribe(topic_list)
        else:
            # Invalid topic format
            if callback_id and _current_runtime:
                _current_runtime.queue_lua_callback(callback_id, 1)  # Error
            return None
        
        if result == mqtt_client.MQTT_ERR_SUCCESS:
            if callback_id and _current_runtime:
                _current_runtime.queue_lua_callback(callback_id, 0)  # Success
            return mid
        else:
            if callback_id and _current_runtime:
                _current_runtime.queue_lua_callback(callback_id, 1)  # Error
            return None
            
    except Exception as e:
        if callback_id and _current_runtime:
            _current_runtime.queue_lua_callback(callback_id, 1)  # Error
        return None


@lua_exporter.export(description="Unsubscribe from MQTT topic", category="mqtt")
def mqtt_client_unsubscribe(client_id: int, topics, options: Optional[Dict[str, Any]] = None, callback_id: Optional[int] = None) -> Optional[int]:
    """
    Unsubscribe from MQTT topic(s)
    
    Args:
        client_id: MQTT client ID
        topics: Topic string or list of topics
        options: Unsubscribe options
        callback_id: Optional callback
        
    Returns:
        Packet ID
    """
    if client_id not in _mqtt_clients:
        if callback_id and _current_runtime:
            _current_runtime.queue_lua_callback(callback_id, 1)  # Error
        return None
    
    client_info = _mqtt_clients[client_id]
    client = client_info['client']
    
    if not client_info['connected']:
        if callback_id and _current_runtime:
            _current_runtime.queue_lua_callback(callback_id, 1)  # Error
        return None
    
    try:
        # Handle single topic or multiple topics
        if isinstance(topics, str):
            result, mid = client.unsubscribe(topics)
        elif isinstance(topics, list):
            # Convert list to topic names only
            topic_list = []
            for topic in topics:
                if isinstance(topic, str):
                    topic_list.append(topic)
                elif isinstance(topic, dict) and 'topic' in topic:
                    topic_list.append(topic['topic'])
                elif isinstance(topic, list) and len(topic) >= 1:
                    topic_list.append(topic[0])
                else:
                    topic_list.append(str(topic))
            
            result, mid = client.unsubscribe(topic_list)
        else:
            if callback_id and _current_runtime:
                _current_runtime.queue_lua_callback(callback_id, 1)  # Error
            return None
        
        if result == mqtt_client.MQTT_ERR_SUCCESS:
            if callback_id and _current_runtime:
                _current_runtime.queue_lua_callback(callback_id, 0)  # Success
            return mid
        else:
            if callback_id and _current_runtime:
                _current_runtime.queue_lua_callback(callback_id, 1)  # Error
            return None
            
    except Exception as e:
        if callback_id and _current_runtime:
            _current_runtime.queue_lua_callback(callback_id, 1)  # Error
        return None


@lua_exporter.export(description="Publish MQTT message", category="mqtt")
def mqtt_client_publish(client_id: int, topic: str, payload: str, options: Optional[Dict[str, Any]] = None, callback_id: Optional[int] = None) -> Optional[int]:
    """
    Publish MQTT message
    
    Args:
        client_id: MQTT client ID
        topic: Topic to publish to
        payload: Message payload
        options: Publish options
        callback_id: Optional callback
        
    Returns:
        Packet ID
    """
    if client_id not in _mqtt_clients:
        if callback_id and _current_runtime:
            _current_runtime.queue_lua_callback(callback_id, 1)  # Error
        return None
    
    client_info = _mqtt_clients[client_id]
    client = client_info['client']
    
    if not client_info['connected']:
        if callback_id and _current_runtime:
            _current_runtime.queue_lua_callback(callback_id, 1)  # Error
        return None
    
    if options is None:
        options = {}
    
    qos = options.get('qos', 0)
    retain = options.get('retain', False)
    
    try:
        result = client.publish(topic, payload, qos=qos, retain=retain)
        
        if result.rc == mqtt_client.MQTT_ERR_SUCCESS:
            if callback_id and _current_runtime:
                _current_runtime.queue_lua_callback(callback_id, 0)  # Success
            return result.mid
        else:
            if callback_id and _current_runtime:
                _current_runtime.queue_lua_callback(callback_id, 1)  # Error
            return None
            
    except Exception as e:
        if callback_id and _current_runtime:
            _current_runtime.queue_lua_callback(callback_id, 1)  # Error
        return None


@lua_exporter.export(description="Add MQTT event listener", category="mqtt")
def mqtt_client_add_event_listener(client_id: int, event_name: str, callback_id: int) -> None:
    """
    Add event listener to MQTT client
    
    Args:
        client_id: MQTT client ID
        event_name: Event name (connected, closed, message, subscribed, unsubscribed, published, error)
        callback_id: Callback function ID
    """
    if client_id not in _mqtt_clients:
        return
    
    client_info = _mqtt_clients[client_id]
    client_info['events'][event_name] = callback_id


@lua_exporter.export(description="Remove MQTT event listener", category="mqtt")
def mqtt_client_remove_event_listener(client_id: int, event_name: str) -> None:
    """
    Remove event listener from MQTT client
    
    Args:
        client_id: MQTT client ID
        event_name: Event name
    """
    if client_id not in _mqtt_clients:
        return
    
    client_info = _mqtt_clients[client_id]
    if event_name in client_info['events']:
        del client_info['events'][event_name]


@lua_exporter.export(description="Check if MQTT client is connected", category="mqtt")
def mqtt_client_is_connected(client_id: int) -> bool:
    """
    Check if MQTT client is connected
    
    Args:
        client_id: MQTT client ID
        
    Returns:
        True if connected, False otherwise
    """
    if client_id not in _mqtt_clients:
        return False
    
    return _mqtt_clients[client_id]['connected']


@lua_exporter.export(description="Get MQTT client info", category="mqtt")
def mqtt_client_get_info(client_id: int) -> Optional[Dict[str, Any]]:
    """
    Get MQTT client information
    
    Args:
        client_id: MQTT client ID
        
    Returns:
        Client info dict or None
    """
    if client_id not in _mqtt_clients:
        return None
    
    client_info = _mqtt_clients[client_id]
    return {
        'connected': client_info['connected'],
        'client_id': client_info['client_id'],
        'host': client_info['host'],
        'port': client_info['port'],
        'use_tls': client_info['use_tls']
    }
