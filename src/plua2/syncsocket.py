"""
Synchronous socket functionality for MobDebug compatibility
Provides LuaSocket-compatible TCP operations for MobDebug debugging support
"""

import socket
import threading
import time
import errno
from typing import Any, Dict, Optional, Tuple, Callable


class SynchronousTCPManager:
    """
    Manages synchronous TCP socket operations for Lua socket compatibility.
    This class provides thread-safe socket operations that are compatible
    with LuaSocket and suitable for use with MobDebug.
    """
    
    def __init__(self, debug_print: Optional[Callable[[str], None]] = None):
        self._sockets: Dict[int, socket.socket] = {}  # Track open sockets
        self._socket_id_counter = 0
        self._socket_lock = threading.Lock()  # Thread safety for socket operations
        self._debug_print = debug_print or (lambda msg: None)  # No-op if no debug function provided
    
    def tcp_connect_sync(self, host: str, port: int) -> Tuple[bool, Optional[int], str]:
        """
        Synchronously connect to a TCP host/port
        
        Args:
            host: Hostname or IP address to connect to
            port: Port number to connect to
            
        Returns:
            (success: bool, connection_id: int|None, message: str)
        """
        # print(f"[PYTHON] tcp_connect_sync: {host}:{port}")
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Set a 1 second connection timeout like your working implementation
            sock.settimeout(1.0)  # 1 second connection timeout
            # print(f"[PYTHON] Attempting connection...")
            sock.connect((host, port))
            # print(f"[PYTHON] Connection successful!")
            
            with self._socket_lock:
                self._socket_id_counter += 1
                conn_id = self._socket_id_counter
                self._sockets[conn_id] = sock
            
            self._debug_print(f"[PYTHON] Connection stored with ID: {conn_id}")
            return True, conn_id, f"Connected to {host}:{port}"
        except Exception as e:
            self._debug_print(f"[PYTHON] Connection failed: {e}")
            return False, None, f"TCP connect error: {str(e)}"

    def tcp_write_sync(self, conn_id: int, data: str) -> Tuple[bool, Optional[int], str]:
        """
        Synchronously write data to a TCP connection
        
        Args:
            conn_id: Connection ID returned from tcp_connect_sync
            data: String data to send
            
        Returns:
            (success: bool, bytes_sent: int|None, message: str)
        """
        self._debug_print(f"[PYTHON] tcp_write_sync: conn_id={conn_id}, data_len={len(data)}")
        try:
            with self._socket_lock:
                sock = self._sockets.get(conn_id)
                if not sock:
                    self._debug_print(f"[PYTHON] Invalid connection ID for write: {conn_id}")
                    return False, None, "Invalid connection ID"
            
            data_bytes = data.encode('utf-8')
            self._debug_print(f"[PYTHON] Sending {len(data_bytes)} bytes...")
            bytes_sent = sock.send(data_bytes)
            self._debug_print(f"[PYTHON] Sent {bytes_sent} bytes successfully")
            return True, bytes_sent, f"Sent {bytes_sent} bytes"
        except Exception as e:
            self._debug_print(f"[PYTHON] Send failed: {e}")
            return False, None, str(e)

    def tcp_read_sync(self, conn_id: int, pattern_or_n: Any = "*l") -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Synchronously read data from a TCP connection with LuaSocket-compatible semantics
        
        Args:
            conn_id: Connection ID returned from tcp_connect_sync
            pattern_or_n: "*l" for line, "*a" for all, number for exact bytes
            
        Returns:
            (success: bool, data: str|None, partial_data: str|None)
            For LuaSocket compatibility: success indicates if full request was satisfied,
            data contains the data if successful, partial_data contains partial data on timeout/error
        """
        self._debug_print(f"[PYTHON] tcp_read_sync: conn_id={conn_id}, pattern={pattern_or_n}")
        try:
            with self._socket_lock:
                sock = self._sockets.get(conn_id)
                if not sock:
                    self._debug_print(f"[PYTHON] Invalid connection ID: {conn_id}")
                    return False, None, None
            
            self._debug_print(f"[PYTHON] Socket found, reading with pattern: {pattern_or_n}")
            
            if pattern_or_n == "*l":
                # Read line (until newline) - LuaSocket compatible, ignore CR
                data = b""
                try:
                    self._debug_print(f"[PYTHON] Reading line...")
                    while True:
                        byte = sock.recv(1)
                        if not byte:
                            # Connection closed
                            self._debug_print(f"[PYTHON] Connection closed during line read")
                            if data:
                                return False, None, data.decode('utf-8', errors='replace')
                            return False, None, None
                        
                        if byte == b"\n":
                            # Found complete line (LF), return line without the LF
                            line = data.decode('utf-8', errors='replace')
                            self._debug_print(f"[PYTHON] Line read complete: '{line}'")
                            return True, line, None
                        elif byte != b"\r":
                            # Ignore CR characters, add all others
                            data += byte
                            
                except BlockingIOError as e:
                    self._debug_print(f"[PYTHON] BlockingIOError during line read: {e}")
                    # Handle non-blocking mode more specifically
                    if hasattr(e, 'errno') and (e.errno == 11 or e.errno == 35):  # EAGAIN or EWOULDBLOCK
                        # No data available, but connection is still open
                        if data:
                            return False, None, data.decode('utf-8', errors='replace')
                        return True, "", None  # No data available (non-blocking socket)
                    else:
                        # Other BlockingIOError
                        if data:
                            return False, None, data.decode('utf-8', errors='replace')
                        return False, None, None
                except socket.timeout:
                    self._debug_print(f"[PYTHON] Timeout during line read")
                    # Timeout occurred
                    if data:
                        return False, None, data.decode('utf-8', errors='replace')
                    return True, "", None  # No data available (timeout)
            
            elif pattern_or_n == "*a":
                # Read all available data until connection closes
                data_parts = []
                try:
                    while True:
                        chunk = sock.recv(4096)  # Read in chunks
                        if not chunk:
                            break  # Connection closed
                        data_parts.append(chunk)
                        
                    if data_parts:
                        data = b"".join(data_parts)
                        return True, data.decode('utf-8', errors='replace'), None
                    else:
                        # Connection closed by peer
                        return False, None, None
                        
                except BlockingIOError:
                    # Non-blocking mode - return what we have so far
                    if data_parts:
                        data = b"".join(data_parts)
                        return True, data.decode('utf-8', errors='replace'), None
                    else:
                        return False, None, None
                except socket.timeout:
                    # Timeout - return what we have so far
                    if data_parts:
                        data = b"".join(data_parts)
                        return True, data.decode('utf-8', errors='replace'), None
                    else:
                        return False, None, None
            
            elif isinstance(pattern_or_n, (int, float)):
                # Read exact number of bytes
                n = int(pattern_or_n)
                if n <= 0:
                    return True, "", None
                    
                data = b""
                remaining = n
                try:
                    while remaining > 0:
                        chunk = sock.recv(remaining)
                        if not chunk:
                            # Connection closed before getting all data
                            if data:
                                return False, None, data.decode('utf-8', errors='replace')
                            return False, None, None
                        data += chunk
                        remaining -= len(chunk)
                    
                    return True, data.decode('utf-8', errors='replace'), None
                    
                except BlockingIOError:
                    # Non-blocking mode
                    if data:
                        return False, None, data.decode('utf-8', errors='replace')
                    return False, None, None
                except socket.timeout:
                    # Timeout occurred
                    if data:
                        return False, None, data.decode('utf-8', errors='replace')
                    return False, None, None
            
            else:
                return False, None, None
                
        except Exception as e:
            return False, None, None

    def tcp_close_sync(self, conn_id: int) -> Tuple[bool, str]:
        """
        Synchronously close a TCP connection
        
        Args:
            conn_id: Connection ID returned from tcp_connect_sync
            
        Returns:
            (success: bool, message: str)
        """
        try:
            with self._socket_lock:
                sock = self._sockets.get(conn_id)
                if not sock:
                    return False, "Invalid connection ID"
                
                sock.close()
                del self._sockets[conn_id]
            
            return True, f"Connection {conn_id} closed"
        except Exception as e:
            return False, str(e)

    def tcp_set_timeout_sync(self, conn_id: int, timeout: Optional[float]) -> Tuple[bool, str]:
        """
        Synchronously set timeout for a TCP connection (LuaSocket compatible)
        
        Args:
            conn_id: Connection ID returned from tcp_connect_sync
            timeout: Timeout in seconds (None for infinite/blocking, 0 for non-blocking)
            
        Returns:
            (success: bool, message: str)
        """
        try:
            with self._socket_lock:
                sock = self._sockets.get(conn_id)
                if not sock:
                    return False, "Invalid connection ID"
                
                # Store the original timeout to restore later if needed
                sock.settimeout(timeout)
                
                if timeout == 0:
                    # Non-blocking mode (LuaSocket compatibility)
                    sock.setblocking(False)
                    timeout_str = "non-blocking mode"
                elif timeout is None:
                    # Infinite timeout / blocking mode (LuaSocket compatibility)
                    sock.setblocking(True)
                    timeout_str = "blocking mode"
                else:
                    # Blocking mode with specific timeout
                    sock.setblocking(True)
                    timeout_str = f"{timeout} seconds"
            
            return True, f"Socket set to {timeout_str} for connection {conn_id}"
        except Exception as e:
            return False, str(e)

    def close_all_connections(self) -> None:
        """
        Close all open connections - useful for cleanup
        """
        with self._socket_lock:
            for conn_id, sock in list(self._sockets.items()):
                try:
                    sock.close()
                except:
                    pass  # Ignore errors during cleanup
            self._sockets.clear()
            
    def get_connection_count(self) -> int:
        """
        Get the number of active connections
        
        Returns:
            Number of active TCP connections
        """
        with self._socket_lock:
            return len(self._sockets)
