"""
UDP functionality for EPLua.

This module provides UDP socket capabilities that can be called from Lua scripts.
"""

import logging
import asyncio
import socket
from typing import Dict, Optional, Tuple
from plua.lua_bindings import export_to_lua, get_global_engine, python_to_lua_table

logger = logging.getLogger(__name__)

# UDP socket management
_udp_sockets: Dict[int, asyncio.DatagramTransport] = {}
_udp_protocols: Dict[int, 'UDPProtocol'] = {}
_udp_socket_counter = 0


class UDPProtocol(asyncio.DatagramProtocol):
    """Custom UDP protocol to handle incoming data"""
    
    def __init__(self, socket_id: int):
        self.socket_id = socket_id
        self.pending_callbacks = []
        self.transport = None
    
    def connection_made(self, transport):
        self.transport = transport
    
    def datagram_received(self, data, addr):
        """Handle incoming UDP datagram"""
        try:
            # Decode the data
            decoded_data = data.decode('utf-8')
            ip, port = addr
            
            # Process all pending receive callbacks
            callbacks_to_process = self.pending_callbacks.copy()
            self.pending_callbacks.clear()
            
            for callback_id in callbacks_to_process:
                result = {
                    'success': True,
                    'data': decoded_data,
                    'ip': ip,
                    'port': port,
                    'error': None
                }
                
                engine = get_global_engine()
                if engine:
                    engine.post_callback_from_thread(callback_id, result)
                    
        except Exception as e:
            logger.error(f"Error in UDP datagram_received: {e}")
            # Send error to all pending callbacks
            for callback_id in self.pending_callbacks:
                result = {
                    'success': False,
                    'data': None,
                    'ip': None,
                    'port': None,
                    'error': str(e)
                }
                
                engine = get_global_engine()
                if engine:
                    engine.post_callback_from_thread(callback_id, result)
            self.pending_callbacks.clear()
    
    def error_received(self, exc):
        """Handle UDP errors"""
        logger.error(f"UDP error received: {exc}")
        # Send error to all pending callbacks
        for callback_id in self.pending_callbacks:
            result = {
                'success': False,
                'data': None,
                'ip': None,
                'port': None,
                'error': str(exc)
            }
            
            engine = get_global_engine()
            if engine:
                engine.post_callback_from_thread(callback_id, result)
        self.pending_callbacks.clear()


@export_to_lua("udp_create_socket")
def udp_create_socket(callback_id: int) -> None:
    """
    Create a UDP socket asynchronously

    Args:
        callback_id: Callback ID to execute when socket creation completes
    """

    async def do_create():
        global _udp_socket_counter
        try:
            _udp_socket_counter += 1
            socket_id = _udp_socket_counter
            
            # Create custom protocol instance
            protocol = UDPProtocol(socket_id)
            
            # Create UDP socket
            transport, _ = await asyncio.get_event_loop().create_datagram_endpoint(
                lambda: protocol,
                local_addr=('0.0.0.0', 0)
            )

            # Store both transport and protocol
            _udp_sockets[socket_id] = transport
            _udp_protocols[socket_id] = protocol

            result = {
                'success': True,
                'socket_id': socket_id,
                'message': 'UDP socket created'
            }

            
            engine = get_global_engine()
            if engine:
                engine.post_callback_from_thread(callback_id, result)

        except Exception as e:
            logger.error(f"Error creating UDP socket: {e}")
            result = {
                'success': False,
                'socket_id': None,
                'message': str(e)
            }

            
            engine = get_global_engine()
            if engine:
                engine.post_callback_from_thread(callback_id, result)

    asyncio.create_task(do_create())


@export_to_lua("udp_send_to")
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
                    'success': False,
                    'error': 'Socket not found'
                }
                
                engine = get_global_engine()
                if engine:
                    engine.post_callback_from_thread(callback_id, result)
                return

            transport = _udp_sockets[socket_id]
            data_bytes = data.encode('utf-8')
            transport.sendto(data_bytes, (host, port))

            result = {
                'success': True,
                'error': None
            }

            
            engine = get_global_engine()
            if engine:
                engine.post_callback_from_thread(callback_id, result)

        except Exception as e:
            logger.error(f"Error sending UDP data: {e}")
            result = {
                'success': False,
                'error': str(e)
            }

            
            engine = get_global_engine()
            if engine:
                engine.post_callback_from_thread(callback_id, result)

    asyncio.create_task(do_send())


@export_to_lua("udp_receive")
def udp_receive(socket_id: int, callback_id: int) -> None:
    """
    Receive data via UDP socket asynchronously

    Args:
        socket_id: Socket ID
        callback_id: Callback ID to execute when receive completes
    """

    async def do_receive():
        try:
            if socket_id not in _udp_protocols:
                result = {
                    'success': False,
                    'data': None,
                    'ip': None,
                    'port': None,
                    'error': 'Socket not found'
                }
                
                engine = get_global_engine()
                if engine:
                    engine.post_callback_from_thread(callback_id, result)
                return

            # Add callback to the protocol's pending callbacks
            # The callback will be triggered when data arrives
            protocol = _udp_protocols[socket_id]
            protocol.pending_callbacks.append(callback_id)

        except Exception as e:
            logger.error(f"Error setting up UDP receive: {e}")
            result = {
                'success': False,
                'data': None,
                'ip': None,
                'port': None,
                'error': str(e)
            }

            
            engine = get_global_engine()
            if engine:
                engine.post_callback_from_thread(callback_id, result)

    asyncio.create_task(do_receive())


@export_to_lua("udp_close")
def udp_close(socket_id: int) -> None:
    """
    Close UDP socket

    Args:
        socket_id: Socket ID
    """
    try:
        if socket_id in _udp_sockets:
            transport = _udp_sockets[socket_id]
            transport.close()
            del _udp_sockets[socket_id]
        
        if socket_id in _udp_protocols:
            del _udp_protocols[socket_id]
            
        logger.info(f"UDP socket {socket_id} closed")
    except Exception as e:
        logger.error(f"Error closing UDP socket {socket_id}: {e}")


@export_to_lua("udp_bind")
def udp_bind(socket_id: int, host: str, port: int, callback_id: int) -> None:
    """
    Bind UDP socket to specific address/port (for server-like functionality)

    Args:
        socket_id: Socket ID
        host: Host to bind to
        port: Port to bind to
        callback_id: Callback ID to execute when bind completes
    """

    async def do_bind():
        try:
            if socket_id not in _udp_sockets:
                result = {
                    'success': False,
                    'message': 'Socket not found'
                }
                
                engine = get_global_engine()
                if engine:
                    engine.post_callback_from_thread(callback_id, result)
                return

            # Close existing socket
            _udp_sockets[socket_id].close()
            
            # Create new protocol
            protocol = UDPProtocol(socket_id)
            
            # Recreate socket bound to specific address
            transport, _ = await asyncio.get_event_loop().create_datagram_endpoint(
                lambda: protocol,
                local_addr=(host, port)
            )

            # Update stored references
            _udp_sockets[socket_id] = transport
            _udp_protocols[socket_id] = protocol

            result = {
                'success': True,
                'message': f'UDP socket bound to {host}:{port}'
            }

            
            engine = get_global_engine()
            if engine:
                engine.post_callback_from_thread(callback_id, result)

        except Exception as e:
            logger.error(f"Error binding UDP socket: {e}")
            result = {
                'success': False,
                'message': str(e)
            }

            
            engine = get_global_engine()
            if engine:
                engine.post_callback_from_thread(callback_id, result)

    asyncio.create_task(do_bind())
