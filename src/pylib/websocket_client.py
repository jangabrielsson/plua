"""
WebSocket functionality for PLua.

This module provides WebSocket client and server capabilities that can be called from Lua scripts.
Features:
- WebSocket client connections (ws:// and wss://)
- WebSocket server endpoints
- Real-time bidirectional communication
- Event-driven message handling
"""

import asyncio
import logging
import ssl
from typing import Dict, Any, Optional
from plua.lua_bindings import export_to_lua, get_global_engine

logger = logging.getLogger(__name__)

# WebSocket connection management
_websocket_connections: Dict[int, Any] = {}
_websocket_connection_counter = 0

# WebSocket server management  
_websocket_servers: Dict[int, Any] = {}
_websocket_server_counter = 0


@export_to_lua("websocket_connect")
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
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE

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

            logger.info(f"WebSocket {conn_id} connected to {url}")

            # Notify connection success
            engine = get_global_engine()
            if engine:
                engine.post_callback_from_thread(callback_id, {
                    'event': 'connected',
                    'conn_id': conn_id,
                    'success': True
                })

            # Start listening for messages
            async def listen_messages():
                try:
                    async for msg in ws:
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            engine = get_global_engine()
                            if engine:
                                engine.post_callback_from_thread(callback_id, {
                                    'event': 'dataReceived',
                                    'conn_id': conn_id,
                                    'data': msg.data
                                })
                        elif msg.type == aiohttp.WSMsgType.BINARY:
                            engine = get_global_engine()
                            if engine:
                                engine.post_callback_from_thread(callback_id, {
                                    'event': 'dataReceived',
                                    'conn_id': conn_id,
                                    'data': msg.data.decode('utf-8', errors='ignore')
                                })
                        elif msg.type == aiohttp.WSMsgType.ERROR:
                            engine = get_global_engine()
                            if engine:
                                engine.post_callback_from_thread(callback_id, {
                                    'event': 'error',
                                    'conn_id': conn_id,
                                    'error': f"WebSocket error: {ws.exception()}"
                                })
                            break
                        elif msg.type == aiohttp.WSMsgType.CLOSE:
                            break

                except Exception as e:
                    logger.error(f"WebSocket {conn_id} exception in message loop: {e}")
                    engine = get_global_engine()
                    if engine:
                        engine.post_callback_from_thread(callback_id, {
                            'event': 'error',
                            'conn_id': conn_id,
                            'error': f"Message listening error: {str(e)}"
                        })
                finally:
                    # Connection closed - handle cleanup
                    if conn_id in _websocket_connections:
                        try:
                            _websocket_connections[conn_id]['connected'] = False
                            await session.close()

                            # Send disconnected event before cleanup
                            engine = get_global_engine()
                            if engine:
                                engine.post_callback_from_thread(callback_id, {
                                    'event': 'disconnected',
                                    'conn_id': conn_id
                                })
                        except Exception as e:
                            logger.error(f"WebSocket {conn_id} error during cleanup: {e}")
                        finally:
                            # Always remove from connections dict
                            if conn_id in _websocket_connections:
                                del _websocket_connections[conn_id]

            # Start the message listener
            asyncio.create_task(listen_messages())

        except Exception as e:
            # Handle connection errors
            logger.error(f"WebSocket {conn_id} connection error: {e}")
            engine = get_global_engine()
            if engine:
                engine.post_callback_from_thread(callback_id, {
                    'event': 'error',
                    'conn_id': conn_id,
                    'error': f"Connection error: {str(e)}",
                    'success': False
                })

    # Start the async connection
    asyncio.create_task(do_connect())
    return conn_id


@export_to_lua("websocket_send")
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
                if callback_id:
                    engine = get_global_engine()
                    if engine:
                        engine.post_callback_from_thread(callback_id, {
                            'success': False,
                            'error': error_msg
                        })
                return

            conn_info = _websocket_connections[conn_id]
            if not conn_info['connected']:
                error_msg = f"WebSocket connection {conn_id} is not connected"
                if callback_id:
                    engine = get_global_engine()
                    if engine:
                        engine.post_callback_from_thread(callback_id, {
                            'success': False,
                            'error': error_msg
                        })
                return

            ws = conn_info['ws']
            await ws.send_str(data)

            # Notify send success
            if callback_id:
                engine = get_global_engine()
                if engine:
                    engine.post_callback_from_thread(callback_id, {
                        'success': True
                    })

        except Exception as e:
            error_msg = f"WebSocket send error: {str(e)}"
            logger.error(error_msg)
            if callback_id:
                engine = get_global_engine()
                if engine:
                    engine.post_callback_from_thread(callback_id, {
                        'success': False,
                        'error': error_msg
                    })

    asyncio.create_task(do_send())


@export_to_lua("websocket_close")
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
                if callback_id:
                    engine = get_global_engine()
                    if engine:
                        engine.post_callback_from_thread(callback_id, {
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
            if callback_id:
                engine = get_global_engine()
                if engine:
                    engine.post_callback_from_thread(callback_id, {
                        'success': True
                    })

        except Exception as e:
            error_msg = f"WebSocket close error: {str(e)}"
            logger.error(error_msg)
            if callback_id:
                engine = get_global_engine()
                if engine:
                    engine.post_callback_from_thread(callback_id, {
                        'success': False,
                        'error': error_msg
                    })

    asyncio.create_task(do_close())


@export_to_lua("websocket_is_open")
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

@export_to_lua("websocket_server_create")
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


@export_to_lua("websocket_server_start")
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
        engine = get_global_engine()
        if engine:
            engine.post_callback_from_thread(callback_id, {
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
        engine = get_global_engine()
        if engine:
            engine.post_callback_from_thread(callback_id, {
                'event': 'connected',
                'server_id': server_id,
                'client_id': client_id
            })

        try:
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    # Notify message received
                    engine = get_global_engine()
                    if engine:
                        engine.post_callback_from_thread(callback_id, {
                            'event': 'receive',
                            'server_id': server_id,
                            'client_id': client_id,
                            'data': msg.data
                        })
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    # Notify error
                    engine = get_global_engine()
                    if engine:
                        engine.post_callback_from_thread(callback_id, {
                            'event': 'error',
                            'server_id': server_id,
                            'client_id': client_id,
                            'error': f'WebSocket error: {ws.exception()}'
                        })
                    break
                elif msg.type == aiohttp.WSMsgType.CLOSE:
                    break
        except Exception as e:
            engine = get_global_engine()
            if engine:
                engine.post_callback_from_thread(callback_id, {
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

            engine = get_global_engine()
            if engine:
                engine.post_callback_from_thread(callback_id, {
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
            engine = get_global_engine()
            if engine:
                engine.post_callback_from_thread(callback_id, {
                    'event': 'started',
                    'server_id': server_id,
                    'host': host,
                    'port': port
                })

        except Exception as e:
            # Notify start error
            logger.error(f"WebSocket server {server_id} start error: {e}")
            engine = get_global_engine()
            if engine:
                engine.post_callback_from_thread(callback_id, {
                    'event': 'error',
                    'server_id': server_id,
                    'error': f'Failed to start server: {str(e)}'
                })

    asyncio.create_task(start_server())


@export_to_lua("websocket_server_send")
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
                if callback_id:
                    engine = get_global_engine()
                    if engine:
                        engine.post_callback_from_thread(callback_id, {
                            'success': False,
                            'error': error_msg
                        })
                return

            server_info = _websocket_servers[server_id]

            if client_id not in server_info['clients']:
                error_msg = f"Client {client_id} not found"
                if callback_id:
                    engine = get_global_engine()
                    if engine:
                        engine.post_callback_from_thread(callback_id, {
                            'success': False,
                            'error': error_msg
                        })
                return

            client_info = server_info['clients'][client_id]
            if not client_info['connected']:
                error_msg = f"Client {client_id} not connected"
                if callback_id:
                    engine = get_global_engine()
                    if engine:
                        engine.post_callback_from_thread(callback_id, {
                            'success': False,
                            'error': error_msg
                        })
                return

            ws = client_info['ws']
            await ws.send_str(data)

            # Notify send success
            if callback_id:
                engine = get_global_engine()
                if engine:
                    engine.post_callback_from_thread(callback_id, {
                        'success': True
                    })

        except Exception as e:
            error_msg = f"Send error: {str(e)}"
            logger.error(error_msg)
            if callback_id:
                engine = get_global_engine()
                if engine:
                    engine.post_callback_from_thread(callback_id, {
                        'success': False,
                        'error': error_msg
                    })

    asyncio.create_task(do_send())


@export_to_lua("websocket_server_stop")
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
                if callback_id:
                    engine = get_global_engine()
                    if engine:
                        engine.post_callback_from_thread(callback_id, {
                            'success': False,
                            'error': error_msg
                        })
                return

            server_info = _websocket_servers[server_id]

            if server_info['server']:
                runner = server_info['server']
                await runner.cleanup()

            # Close all client connections
            for client_info in server_info['clients'].values():
                try:
                    if client_info['connected']:
                        await client_info['ws'].close()
                except Exception as e:
                    logger.error(f"Error closing client WebSocket: {e}")

            server_info['running'] = False
            server_info['server'] = None
            server_info['clients'] = {}

            # Remove from servers dict
            if server_id in _websocket_servers:
                del _websocket_servers[server_id]

            # Notify stop success
            if callback_id:
                engine = get_global_engine()
                if engine:
                    engine.post_callback_from_thread(callback_id, {
                        'success': True
                    })

        except Exception as e:
            error_msg = f"Server stop error: {str(e)}"
            logger.error(error_msg)
            if callback_id:
                engine = get_global_engine()
                if engine:
                    engine.post_callback_from_thread(callback_id, {
                        'success': False,
                        'error': error_msg
                    })

    asyncio.create_task(do_stop())


@export_to_lua("websocket_server_is_running")
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
