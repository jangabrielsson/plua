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
