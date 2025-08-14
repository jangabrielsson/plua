"""
TCP functionality for PLua.

This module provides TCP socket capabilities that can be called from Lua scripts.
Supports async TCP client connections, TCP servers, and connection management.
"""

import logging
import asyncio
from typing import Dict, Tuple, Optional
from plua.lua_bindings import export_to_lua, get_global_engine, python_to_lua_table

logger = logging.getLogger(__name__)

# Connection management
_tcp_connections: Dict[int, Tuple[asyncio.StreamReader, asyncio.StreamWriter]] = {}
_tcp_connection_counter = 0

# Server management  
_tcp_servers: Dict[int, asyncio.Server] = {}
_tcp_server_counter = 0


@export_to_lua("tcp_connect")
def tcp_connect(host: str, port: int, callback_id: int) -> None:
    """
    Connect to a TCP server asynchronously.
    
    Args:
        host: Server hostname or IP
        port: Server port  
        callback_id: Callback ID to execute when connection completes
    """
    
    async def do_connect():
        global _tcp_connection_counter
        engine = get_global_engine()
        if not engine:
            logger.error("No global engine available for TCP connect callback")
            return
            
        try:
            reader, writer = await asyncio.open_connection(host, port)
            
            # Store connection with unique ID
            _tcp_connection_counter += 1
            conn_id = _tcp_connection_counter
            _tcp_connections[conn_id] = (reader, writer)
            
            # Success result
            result = {
                'success': True,
                'conn_id': conn_id,
                'message': f'Connected to {host}:{port}'
            }
            
            # Call back to Lua
            lua_result = python_to_lua_table(result)
            engine._lua.globals()["_PY"]["timerExpired"](callback_id, lua_result)
            
            logger.debug(f"TCP connected to {host}:{port} with conn_id {conn_id}")
            
        except Exception as e:
            # Error result
            result = {
                'success': False,
                'conn_id': None,
                'message': str(e)
            }
            
            try:
                lua_result = python_to_lua_table(result)
                engine._lua.globals()["_PY"]["timerExpired"](callback_id, lua_result)
            except Exception as callback_err:
                logger.error(f"Error calling TCP connect callback {callback_id}: {callback_err}")
            
            logger.error(f"TCP connect error to {host}:{port}: {e}")
    
    asyncio.create_task(do_connect())


@export_to_lua("tcp_read")
def tcp_read(conn_id: int, max_bytes: int, callback_id: int) -> None:
    """
    Read data from TCP connection asynchronously.
    
    Args:
        conn_id: Connection ID
        max_bytes: Maximum bytes to read
        callback_id: Callback ID to execute when read completes
    """
    
    async def do_read():
        engine = get_global_engine()
        if not engine:
            logger.error("No global engine available for TCP read callback")
            return
            
        try:
            if conn_id not in _tcp_connections:
                result = {
                    'success': False,
                    'data': None,
                    'message': 'Connection not found'
                }
                lua_result = python_to_lua_table(result)
                engine._lua.globals()["_PY"]["timerExpired"](callback_id, lua_result)
                return
            
            reader, writer = _tcp_connections[conn_id]
            
            # Read data using the reader
            data = await reader.read(max_bytes)
            
            result = {
                'success': True,
                'data': data.decode('utf-8', errors='replace'),
                'message': None
            }
            
            lua_result = python_to_lua_table(result)
            engine._lua.globals()["_PY"]["timerExpired"](callback_id, lua_result)
            
            logger.debug(f"TCP read {len(data)} bytes from conn_id {conn_id}")
            
        except Exception as e:
            result = {
                'success': False,
                'data': None,
                'message': str(e)
            }
            
            try:
                lua_result = python_to_lua_table(result)
                engine._lua.globals()["_PY"]["timerExpired"](callback_id, lua_result)
            except Exception as callback_err:
                logger.error(f"Error calling TCP read callback {callback_id}: {callback_err}")
            
            logger.error(f"TCP read error for conn_id {conn_id}: {e}")
    
    asyncio.create_task(do_read())


@export_to_lua("tcp_read_until")
def tcp_read_until(conn_id: int, delimiter: str, max_bytes: int, callback_id: int) -> None:
    """
    Read data from TCP connection until delimiter is found.
    
    Args:
        conn_id: Connection ID
        delimiter: Delimiter to read until
        max_bytes: Maximum bytes to read
        callback_id: Callback ID to execute when read completes
    """
    
    async def do_read_until():
        engine = get_global_engine()
        if not engine:
            logger.error("No global engine available for TCP read_until callback")
            return
            
        try:
            if conn_id not in _tcp_connections:
                result = {
                    'success': False,
                    'data': None,
                    'message': 'Connection not found'
                }
                lua_result = python_to_lua_table(result)
                engine._lua.globals()["_PY"]["timerExpired"](callback_id, lua_result)
                return
            
            reader, writer = _tcp_connections[conn_id]
            
            # Read until delimiter
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
            
            lua_result = python_to_lua_table(result)
            engine._lua.globals()["_PY"]["timerExpired"](callback_id, lua_result)
            
            logger.debug(f"TCP read_until {len(buffer)} bytes from conn_id {conn_id}")
            
        except Exception as e:
            result = {
                'success': False,
                'data': None,
                'message': str(e)
            }
            
            try:
                lua_result = python_to_lua_table(result)
                engine._lua.globals()["_PY"]["timerExpired"](callback_id, lua_result)
            except Exception as callback_err:
                logger.error(f"Error calling TCP read_until callback {callback_id}: {callback_err}")
            
            logger.error(f"TCP read_until error for conn_id {conn_id}: {e}")
    
    asyncio.create_task(do_read_until())


@export_to_lua("tcp_write")
def tcp_write(conn_id: int, data: str, callback_id: int) -> None:
    """
    Write data to TCP connection asynchronously.
    
    Args:
        conn_id: Connection ID
        data: Data to write
        callback_id: Callback ID to execute when write completes
    """
    
    async def do_write():
        engine = get_global_engine()
        if not engine:
            logger.error("No global engine available for TCP write callback")
            return
            
        try:
            if conn_id not in _tcp_connections:
                result = {
                    'success': False,
                    'bytes_written': 0,
                    'message': 'Connection not found'
                }
                lua_result = python_to_lua_table(result)
                engine._lua.globals()["_PY"]["timerExpired"](callback_id, lua_result)
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
            
            lua_result = python_to_lua_table(result)
            engine._lua.globals()["_PY"]["timerExpired"](callback_id, lua_result)
            
            logger.debug(f"TCP wrote {len(data_bytes)} bytes to conn_id {conn_id}")
            
        except Exception as e:
            result = {
                'success': False,
                'bytes_written': 0,
                'message': str(e)
            }
            
            try:
                lua_result = python_to_lua_table(result)
                engine._lua.globals()["_PY"]["timerExpired"](callback_id, lua_result)
            except Exception as callback_err:
                logger.error(f"Error calling TCP write callback {callback_id}: {callback_err}")
            
            logger.error(f"TCP write error for conn_id {conn_id}: {e}")
    
    asyncio.create_task(do_write())


@export_to_lua("tcp_close")
def tcp_close(conn_id: int, callback_id: int) -> None:
    """
    Close TCP connection asynchronously.
    
    Args:
        conn_id: Connection ID
        callback_id: Callback ID to execute when close completes
    """
    
    async def do_close():
        engine = get_global_engine()
        if not engine:
            logger.error("No global engine available for TCP close callback")
            return
            
        try:
            if conn_id not in _tcp_connections:
                result = {
                    'success': False,
                    'message': 'Connection not found'
                }
                lua_result = python_to_lua_table(result)
                engine._lua.globals()["_PY"]["timerExpired"](callback_id, lua_result)
                return
            
            reader, writer = _tcp_connections[conn_id]
            writer.close()
            await writer.wait_closed()
            del _tcp_connections[conn_id]
            
            result = {
                'success': True,
                'message': 'Connection closed'
            }
            
            lua_result = python_to_lua_table(result)
            engine._lua.globals()["_PY"]["timerExpired"](callback_id, lua_result)
            
            logger.debug(f"TCP closed conn_id {conn_id}")
            
        except Exception as e:
            result = {
                'success': False,
                'message': str(e)
            }
            
            try:
                lua_result = python_to_lua_table(result)
                engine._lua.globals()["_PY"]["timerExpired"](callback_id, lua_result)
            except Exception as callback_err:
                logger.error(f"Error calling TCP close callback {callback_id}: {callback_err}")
            
            logger.error(f"TCP close error for conn_id {conn_id}: {e}")
    
    asyncio.create_task(do_close())


@export_to_lua("tcp_server_create")
def tcp_server_create() -> int:
    """
    Create a TCP server instance.
    
    Returns:
        Server ID for the created server
    """
    global _tcp_server_counter
    _tcp_server_counter += 1
    server_id = _tcp_server_counter
    logger.debug(f"TCP server created with ID {server_id}")
    return server_id


@export_to_lua("tcp_server_start")
def tcp_server_start(server_id: int, host: str, port: int, callback_id: int) -> None:
    """
    Start TCP server listening on host:port.
    
    Args:
        server_id: Server ID
        host: Host to bind to
        port: Port to bind to  
        callback_id: Callback ID to execute when clients connect (persistent)
    """
    
    async def handle_client(reader, writer):
        """Handle individual client connections"""
        global _tcp_connection_counter
        engine = get_global_engine()
        if not engine:
            logger.error("No global engine available for TCP server client callback")
            return
            
        try:
            # Get client information
            peername = writer.get_extra_info('peername')
            client_ip = peername[0] if peername else 'unknown'
            client_port = peername[1] if peername else 0
            
            # Store the client connection like a regular TCP connection
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
            
            lua_result = python_to_lua_table(result)
            engine._lua.globals()["_PY"]["timerExpired"](callback_id, lua_result)
            
            logger.debug(f"TCP server accepted client {client_ip}:{client_port} as conn_id {conn_id}")
            
        except Exception as e:
            # Handle client connection errors
            result = {
                'success': False,
                'conn_id': None,
                'client_ip': None,
                'client_port': None,
                'error': str(e)
            }
            
            try:
                lua_result = python_to_lua_table(result)
                engine._lua.globals()["_PY"]["timerExpired"](callback_id, lua_result)
            except Exception as callback_err:
                logger.error(f"Error calling TCP server client callback {callback_id}: {callback_err}")
            
            logger.error(f"TCP server client connection error: {e}")
    
    async def start_server():
        engine = get_global_engine()
        if not engine:
            logger.error("No global engine available for TCP server start")
            return
            
        try:
            # Create and start the server
            server = await asyncio.start_server(handle_client, host, port)
            _tcp_servers[server_id] = server
            
            logger.info(f"TCP server {server_id} started on {host}:{port}")
            
        except Exception as e:
            logger.error(f"TCP server start error: {e}")
    
    asyncio.create_task(start_server())


@export_to_lua("tcp_server_stop")
def tcp_server_stop(server_id: int, callback_id: int) -> None:
    """
    Stop TCP server.
    
    Args:
        server_id: Server ID
        callback_id: Callback ID to execute when server stops
    """
    
    async def stop_server():
        engine = get_global_engine()
        if not engine:
            logger.error("No global engine available for TCP server stop callback")
            return
            
        try:
            if server_id in _tcp_servers:
                server = _tcp_servers[server_id]
                server.close()
                await server.wait_closed()
                del _tcp_servers[server_id]
                
                result = {
                    'success': True,
                    'message': f'TCP server {server_id} stopped'
                }
                
                logger.info(f"TCP server {server_id} stopped")
            else:
                result = {
                    'success': False,
                    'message': f'TCP server {server_id} not found'
                }
            
            lua_result = python_to_lua_table(result)
            engine._lua.globals()["_PY"]["timerExpired"](callback_id, lua_result)
            
        except Exception as e:
            result = {
                'success': False,
                'message': str(e)
            }
            
            try:
                lua_result = python_to_lua_table(result)
                engine._lua.globals()["_PY"]["timerExpired"](callback_id, lua_result)
            except Exception as callback_err:
                logger.error(f"Error calling TCP server stop callback {callback_id}: {callback_err}")
            
            logger.error(f"TCP server stop error: {e}")
    
    asyncio.create_task(stop_server())
