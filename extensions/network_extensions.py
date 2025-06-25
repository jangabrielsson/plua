"""
Asyncio-based Network Extensions for PLua
Provides true async TCP/UDP networking with Lua callback support
"""

import asyncio
import socket
import threading
from .registry import registry
import urllib.request
import urllib.parse
import urllib.error
from urllib.parse import urlparse
import ssl
import lupa


# --- Event Loop Manager ---
class AsyncioLoopManager:
    """Ensures a running asyncio event loop, even if main thread is blocked"""

    def __init__(self):
        self.loop = None
        self.thread = None
        # Don't start the loop immediately - only when needed

    def _ensure_loop(self):
        if self.loop is None or self.loop.is_closed():
            self.loop = asyncio.new_event_loop()
            self.thread = threading.Thread(target=self._run_loop, daemon=False)
            self.thread.start()

    def _run_loop(self):
        asyncio.set_event_loop(self.loop)
        try:
            self.loop.run_forever()
        except Exception:
            pass  # Ignore exceptions during shutdown

    def get_loop(self):
        self._ensure_loop()
        return self.loop

    def shutdown(self):
        """Clean shutdown of the event loop"""
        if self.loop and not self.loop.is_closed():
            try:
                # Cancel all pending tasks
                pending = asyncio.all_tasks(self.loop)
                for task in pending:
                    task.cancel()

                # Stop the loop
                self.loop.call_soon_threadsafe(self.loop.stop)

                # Wait for thread to finish (with timeout)
                if self.thread and self.thread.is_alive():
                    self.thread.join(timeout=1.0)

                # Close the loop
                self.loop.close()
            except Exception:
                pass  # Ignore errors during shutdown

    def stop_loop(self):
        """Stop the event loop gracefully"""
        if self.loop and not self.loop.is_closed():
            self.loop.call_soon_threadsafe(self.loop.stop)


loop_manager = AsyncioLoopManager()


# --- Asyncio Network Manager ---
class AsyncioNetworkManager:
    def __init__(self):
        self.tcp_connections = {}  # conn_id: (reader, writer)
        self.udp_transports = {}  # conn_id: transport
        self.next_id = 1
        self.lock = threading.Lock()
        self.active_operations = 0  # Track active operations
        self.active_callbacks = 0  # Track active callbacks

    def _next_conn_id(self):
        with self.lock:
            cid = self.next_id
            self.next_id += 1
            return cid

    def _increment_operations(self):
        with self.lock:
            self.active_operations += 1

    def _decrement_operations(self):
        with self.lock:
            self.active_operations -= 1
        # Only stop the loop if no active operations AND no open connections AND no active callbacks
        if (
            self.active_operations <= 0
            and len(self.tcp_connections) == 0
            and len(self.udp_transports) == 0
            and self.active_callbacks <= 0
        ):
            # No more active operations, connections, or callbacks, signal shutdown
            loop_manager.stop_loop()

    def _increment_callbacks(self):
        """Increment the callback counter when starting an async operation with callback"""
        with self.lock:
            self.active_callbacks += 1

    def _decrement_callbacks(self):
        """Decrement the callback counter when a callback completes"""
        with self.lock:
            self.active_callbacks -= 1
        # Only stop the loop if no active operations AND no open connections AND no active callbacks
        if (
            self.active_operations <= 0
            and len(self.tcp_connections) == 0
            and len(self.udp_transports) == 0
            and self.active_callbacks <= 0
        ):
            # No more active operations, connections, or callbacks, signal shutdown
            loop_manager.stop_loop()

    def has_active_operations(self):
        """Check if there are any active network operations or callbacks"""
        with self.lock:
            return (
                self.active_operations > 0
                or len(self.tcp_connections) > 0
                or len(self.udp_transports) > 0
                or self.active_callbacks > 0
            )

    def force_cleanup(self):
        """Force cleanup of all operations and connections"""
        with self.lock:
            # Close all TCP connections
            for conn_id in list(self.tcp_connections.keys()):
                try:
                    reader, writer = self.tcp_connections[conn_id]
                    if writer:
                        writer.close()
                except Exception:
                    pass
            self.tcp_connections.clear()

            # Close all UDP transports
            for conn_id in list(self.udp_transports.keys()):
                try:
                    transport = self.udp_transports[conn_id]
                    if transport:
                        transport.close()
                except Exception:
                    pass
            self.udp_transports.clear()

            # Reset operation counters
            self.active_operations = 0
            self.active_callbacks = 0

    # --- TCP ---
    def tcp_connect(self, host, port, callback):
        # Try synchronous approach first to avoid atexit issues
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)  # 10 second timeout
            sock.connect((host, port))

            # Store connection
            conn_id = self._next_conn_id()
            self.tcp_connections[conn_id] = (
                sock,
                sock,
            )  # Use sock for both reader/writer
            callback(True, conn_id, f"Connected to {host}:{port}")

        except Exception as e:
            callback(False, None, f"TCP connect error: {str(e)}")

    async def tcp_write_async(self, conn_id, data, callback):
        self._increment_operations()
        try:
            reader, writer = self.tcp_connections.get(conn_id, (None, None))
            if not writer:
                loop_manager.get_loop().call_soon_threadsafe(
                    callback, False, None, f"TCP connection {conn_id} not found"
                )
                return
            if isinstance(data, str):
                data_bytes = data.encode("utf-8")
            else:
                data_bytes = bytes(data)
            writer.write(data_bytes)
            await writer.drain()
            loop_manager.get_loop().call_soon_threadsafe(
                callback, True, len(data_bytes), f"Sent {len(data_bytes)} bytes"
            )
        except Exception as e:
            loop_manager.get_loop().call_soon_threadsafe(
                callback, False, None, f"TCP write error: {str(e)}"
            )
        finally:
            self._decrement_operations()

    def tcp_write(self, conn_id, data, callback):
        # Use create_task to properly handle the coroutine
        task = asyncio.run_coroutine_threadsafe(
            self.tcp_write_async(conn_id, data, callback), loop_manager.get_loop()
        )
        task.add_done_callback(lambda t: None)

    async def tcp_read_async(self, conn_id, max_bytes, callback):
        self._increment_operations()
        try:
            reader, writer = self.tcp_connections.get(conn_id, (None, None))
            if not reader:
                loop_manager.get_loop().call_soon_threadsafe(
                    callback, False, None, f"TCP connection {conn_id} not found"
                )
                return
            data = await reader.read(max_bytes)
            if data:
                data_str = data.decode("utf-8", errors="ignore")
                loop_manager.get_loop().call_soon_threadsafe(
                    callback, True, data_str, f"Received {len(data)} bytes"
                )
            else:
                loop_manager.get_loop().call_soon_threadsafe(
                    callback, False, None, "Connection closed by peer"
                )
                self.tcp_connections.pop(conn_id, None)
        except socket.timeout:
            # Don't remove connection for timeout errors (including non-blocking)
            return (
                False,
                None,
                "TCP read error: [Errno 35] Resource temporarily unavailable",
            )
        except BlockingIOError as e:
            # Don't remove connection for non-blocking errors (Errno 35/36)
            if hasattr(e, "errno") and e.errno in [
                35,
                36,
            ]:  # Resource temporarily unavailable / Operation now in progress
                return (
                    False,
                    None,
                    "TCP read error: [Errno 35] Resource temporarily unavailable",
                )
            else:
                # Other BlockingIOError, remove connection
                self.tcp_connections.pop(conn_id, None)
                return False, None, f"TCP read error: {str(e)}"
        except ConnectionError as e:
            # Remove connection for actual connection errors
            self.tcp_connections.pop(conn_id, None)
            return False, None, f"TCP connection error: {str(e)}"
        except Exception as e:
            # Remove connection for other unexpected errors
            self.tcp_connections.pop(conn_id, None)
            return False, None, f"TCP read error: {str(e)}"
        finally:
            self._decrement_operations()

    def tcp_read(self, conn_id, max_bytes, callback):
        # Use create_task to properly handle the coroutine
        task = asyncio.run_coroutine_threadsafe(
            self.tcp_read_async(conn_id, max_bytes, callback), loop_manager.get_loop()
        )
        task.add_done_callback(lambda t: None)

    async def tcp_close_async(self, conn_id, callback):
        self._increment_operations()
        try:
            reader, writer = self.tcp_connections.pop(conn_id, (None, None))
            if writer:
                writer.close()
                await writer.wait_closed()
                loop_manager.get_loop().call_soon_threadsafe(
                    callback, True, f"Connection {conn_id} closed"
                )
            else:
                loop_manager.get_loop().call_soon_threadsafe(
                    callback, False, f"Connection {conn_id} not found"
                )
        except Exception as e:
            loop_manager.get_loop().call_soon_threadsafe(
                callback, False, f"Close error: {str(e)}"
            )
        finally:
            self._decrement_operations()

    def tcp_close(self, conn_id, callback):
        # Use create_task to properly handle the coroutine
        task = asyncio.run_coroutine_threadsafe(
            self.tcp_close_async(conn_id, callback), loop_manager.get_loop()
        )
        task.add_done_callback(lambda t: None)

    # --- Synchronous TCP Functions ---
    def tcp_connect_sync(self, host, port):
        """Synchronous TCP connect - returns (success, conn_id, message)"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)  # 10 second timeout
            sock.connect((host, port))

            # Store connection
            conn_id = self._next_conn_id()
            self.tcp_connections[conn_id] = (
                sock,
                sock,
            )  # Use sock for both reader/writer
            return True, conn_id, f"Connected to {host}:{port}"

        except Exception as e:
            return False, None, f"TCP connect error: {str(e)}"

    def tcp_write_sync(self, conn_id, data):
        """Synchronous TCP write - returns (success, bytes_written, message)"""
        try:
            reader, writer = self.tcp_connections.get(conn_id, (None, None))
            if not writer:
                return False, None, f"TCP connection {conn_id} not found"

            if isinstance(data, str):
                data_bytes = data.encode("utf-8")
            else:
                data_bytes = bytes(data)

            writer.send(data_bytes)
            return True, len(data_bytes), f"Sent {len(data_bytes)} bytes"

        except Exception as e:
            return False, None, f"TCP write error: {str(e)}"

    def tcp_read_sync(self, conn_id, pattern):
        """Read data from TCP connection and return (success, data, message)"""
        try:
            reader, writer = self.tcp_connections.get(conn_id, (None, None))
            if not reader:
                return False, None, f"TCP connection {conn_id} not found"

            sock = reader

            # Handle different patterns
            if pattern == "*a":
                # Read all data until connection is closed
                data_parts = []
                while True:
                    chunk = sock.recv(4096)  # Read in chunks
                    if not chunk:
                        break  # Connection closed
                    data_parts.append(chunk)

                if data_parts:
                    data = b"".join(data_parts)
                    data_str = data.decode("utf-8", errors="ignore")
                    return True, data_str, f"Received {len(data)} bytes (all data)"
                else:
                    # Connection closed by peer
                    self.tcp_connections.pop(conn_id, None)
                    return False, None, "Connection closed by peer"

            elif pattern == "*l":
                # Read a line (terminated by LF, CR ignored)
                line_parts = []
                while True:
                    char = sock.recv(1)
                    if not char:
                        # Connection closed
                        self.tcp_connections.pop(conn_id, None)
                        if line_parts:
                            line = b"".join(line_parts).decode("utf-8", errors="ignore")
                            return True, line, f"Received line ({len(line)} chars)"
                        else:
                            return False, None, "Connection closed by peer"

                    if char == b"\n":
                        # End of line found
                        line = b"".join(line_parts).decode("utf-8", errors="ignore")
                        return True, line, f"Received line ({len(line)} chars)"
                    elif char != b"\r":
                        # Ignore CR characters, add all others
                        line_parts.append(char)

            elif isinstance(pattern, (int, float)):
                # Read specified number of bytes
                max_bytes = int(pattern)
                data = sock.recv(max_bytes)
                if data:
                    data_str = data.decode("utf-8", errors="ignore")
                    return True, data_str, f"Received {len(data)} bytes"
                else:
                    # Connection closed by peer
                    self.tcp_connections.pop(conn_id, None)
                    return False, None, "Connection closed by peer"
            else:
                return (
                    False,
                    None,
                    f"Invalid pattern: {pattern}. Use '*a', '*l', or a number",
                )

        except socket.timeout:
            # Don't remove connection for timeout errors (including non-blocking)
            return True, "", "No data available (non-blocking socket)"
        except BlockingIOError as e:
            # Don't remove connection for non-blocking errors (Errno 35/36)
            if hasattr(e, "errno") and e.errno in [
                35,
                36,
            ]:  # Resource temporarily unavailable / Operation now in progress
                return True, "", "No data available (non-blocking socket)"
            else:
                # Other BlockingIOError, remove connection
                self.tcp_connections.pop(conn_id, None)
                return False, None, f"TCP read error: {str(e)}"
        except ConnectionError as e:
            # Remove connection for actual connection errors
            self.tcp_connections.pop(conn_id, None)
            return False, None, f"TCP connection error: {str(e)}"
        except Exception as e:
            # Remove connection for other unexpected errors
            self.tcp_connections.pop(conn_id, None)
            return False, None, f"TCP read error: {str(e)}"

    def tcp_close_sync(self, conn_id):
        """Synchronous TCP close - returns (success, message)"""
        try:
            reader, writer = self.tcp_connections.pop(conn_id, (None, None))
            if writer:
                writer.close()
                return True, f"Connection {conn_id} closed"
            else:
                return False, f"Connection {conn_id} not found"
        except Exception as e:
            return False, f"TCP close error: {str(e)}"

    def tcp_set_timeout_sync(self, conn_id, timeout_seconds):
        """Synchronous TCP timeout setter - returns (success, message)"""
        try:
            reader, writer = self.tcp_connections.get(conn_id, (None, None))
            if not reader or not writer:
                return False, f"TCP connection {conn_id} not found"

            # Both reader and writer are the same socket object
            sock = reader
            sock.settimeout(timeout_seconds)

            if timeout_seconds is None:
                return True, f"Socket set to blocking mode for connection {conn_id}"
            elif timeout_seconds == 0:
                return True, f"Socket set to non-blocking mode for connection {conn_id}"
            else:
                return (
                    True,
                    f"Timeout set to {timeout_seconds} seconds for connection {conn_id}",
                )

        except Exception as e:
            return False, f"TCP timeout set error: {str(e)}"

    def tcp_get_timeout_sync(self, conn_id):
        """Synchronous TCP timeout getter - returns (success, timeout_seconds, message)"""
        try:
            reader, writer = self.tcp_connections.get(conn_id, (None, None))
            if not reader or not writer:
                return False, None, f"TCP connection {conn_id} not found"

            # Both reader and writer are the same socket object
            sock = reader
            timeout = sock.gettimeout()

            if timeout is None:
                return (
                    True,
                    timeout,
                    f"Socket is in blocking mode for connection {conn_id}",
                )
            elif timeout == 0:
                return (
                    True,
                    timeout,
                    f"Socket is in non-blocking mode for connection {conn_id}",
                )
            else:
                return (
                    True,
                    timeout,
                    f"Current timeout: {timeout} seconds for connection {conn_id}",
                )

        except Exception as e:
            return False, None, f"TCP timeout get error: {str(e)}"

    # --- Asynchronous TCP Timeout Functions ---
    async def tcp_set_timeout_async(self, conn_id, timeout_seconds, callback):
        self._increment_operations()
        try:
            reader, writer = self.tcp_connections.get(conn_id, (None, None))
            if not reader or not writer:
                loop_manager.get_loop().call_soon_threadsafe(
                    callback, False, f"TCP connection {conn_id} not found"
                )
                return

            # Both reader and writer are the same socket object
            sock = reader
            sock.settimeout(timeout_seconds)

            if timeout_seconds is None:
                loop_manager.get_loop().call_soon_threadsafe(
                    callback,
                    True,
                    f"Socket set to blocking mode for connection {conn_id}",
                )
            elif timeout_seconds == 0:
                loop_manager.get_loop().call_soon_threadsafe(
                    callback,
                    True,
                    f"Socket set to non-blocking mode for connection {conn_id}",
                )
            else:
                loop_manager.get_loop().call_soon_threadsafe(
                    callback,
                    True,
                    f"Timeout set to {timeout_seconds} seconds for connection {conn_id}",
                )

        except Exception as e:
            loop_manager.get_loop().call_soon_threadsafe(
                callback, False, f"TCP timeout set error: {str(e)}"
            )
        finally:
            self._decrement_operations()

    def tcp_set_timeout(self, conn_id, timeout_seconds, callback):
        """Asynchronous TCP timeout setter"""
        task = asyncio.run_coroutine_threadsafe(
            self.tcp_set_timeout_async(conn_id, timeout_seconds, callback),
            loop_manager.get_loop(),
        )
        task.add_done_callback(lambda t: None)

    async def tcp_get_timeout_async(self, conn_id, callback):
        self._increment_operations()
        try:
            reader, writer = self.tcp_connections.get(conn_id, (None, None))
            if not reader or not writer:
                loop_manager.get_loop().call_soon_threadsafe(
                    callback, False, None, f"TCP connection {conn_id} not found"
                )
                return

            # Both reader and writer are the same socket object
            sock = reader
            timeout = sock.gettimeout()

            if timeout is None:
                loop_manager.get_loop().call_soon_threadsafe(
                    callback,
                    True,
                    timeout,
                    f"Socket is in blocking mode for connection {conn_id}",
                )
            elif timeout == 0:
                loop_manager.get_loop().call_soon_threadsafe(
                    callback,
                    True,
                    timeout,
                    f"Socket is in non-blocking mode for connection {conn_id}",
                )
            else:
                loop_manager.get_loop().call_soon_threadsafe(
                    callback,
                    True,
                    timeout,
                    f"Current timeout: {timeout} seconds for connection {conn_id}",
                )

        except Exception as e:
            loop_manager.get_loop().call_soon_threadsafe(
                callback, False, None, f"TCP timeout get error: {str(e)}"
            )
        finally:
            self._decrement_operations()

    def tcp_get_timeout(self, conn_id, callback):
        """Asynchronous TCP timeout getter"""
        task = asyncio.run_coroutine_threadsafe(
            self.tcp_get_timeout_async(conn_id, callback), loop_manager.get_loop()
        )
        task.add_done_callback(lambda t: None)

    # --- UDP ---
    class UDPProtocol(asyncio.DatagramProtocol):
        def __init__(self, conn_id, callback, manager):
            self.conn_id = conn_id
            self.callback = callback
            self.manager = manager
            self.transport = None

        def connection_made(self, transport):
            self.transport = transport
            loop_manager.get_loop().call_soon_threadsafe(
                self.callback,
                True,
                self.conn_id,
                f"UDP connected (conn_id={self.conn_id})",
            )

        def datagram_received(self, data, addr):
            # Not used in this demo, but could be extended
            pass

        def error_received(self, exc):
            loop_manager.get_loop().call_soon_threadsafe(
                self.callback, False, self.conn_id, f"UDP error: {exc}"
            )

        def connection_lost(self, exc):
            self.manager.udp_transports.pop(self.conn_id, None)

    def udp_connect(self, host, port, callback):
        """Connect to UDP server asynchronously"""
        self._increment_operations()

        async def udp_connect_async():
            try:
                conn_id = self._next_conn_id()
                loop = loop_manager.get_loop()
                transport, protocol = await loop.create_datagram_endpoint(
                    lambda: self.UDPProtocol(conn_id, callback, self),
                    remote_addr=(host, port),
                )
                self.udp_transports[conn_id] = transport
            except Exception as e:
                loop_manager.get_loop().call_soon_threadsafe(
                    callback, False, None, f"UDP connect error: {str(e)}"
                )
            finally:
                self._decrement_operations()

        # Use create_task to properly handle the coroutine
        task = asyncio.run_coroutine_threadsafe(
            udp_connect_async(), loop_manager.get_loop()
        )
        task.add_done_callback(lambda t: None)

    def udp_write(self, conn_id, data, host, port, callback):
        """Write data to UDP connection asynchronously"""
        self._increment_operations()

        async def udp_write_async():
            try:
                transport = self.udp_transports.get(conn_id)
                if not transport:
                    loop_manager.get_loop().call_soon_threadsafe(
                        callback, False, None, f"UDP connection {conn_id} not found"
                    )
                    return
                if isinstance(data, str):
                    data_bytes = data.encode("utf-8")
                else:
                    data_bytes = bytes(data)
                transport.sendto(data_bytes, (host, port))
                loop_manager.get_loop().call_soon_threadsafe(
                    callback,
                    True,
                    len(data_bytes),
                    f"Sent {len(data_bytes)} bytes to {host}:{port}",
                )
            except Exception as e:
                loop_manager.get_loop().call_soon_threadsafe(
                    callback, False, None, f"UDP write error: {str(e)}"
                )
            finally:
                self._decrement_operations()

        # Use create_task to properly handle the coroutine
        task = asyncio.run_coroutine_threadsafe(
            udp_write_async(), loop_manager.get_loop()
        )
        task.add_done_callback(lambda t: None)

    def udp_read(self, conn_id, max_bytes, callback):
        """Read data from UDP connection asynchronously"""
        self._increment_operations()

        async def udp_read_async():
            try:
                transport = self.udp_transports.get(conn_id)
                if not transport:
                    loop_manager.get_loop().call_soon_threadsafe(
                        callback, False, None, f"UDP connection {conn_id} not found"
                    )
                    return

                # Create a future to wait for data
                loop = loop_manager.get_loop()
                future = loop.create_future()

                def datagram_received(data, addr):
                    if not future.done():
                        future.set_result((data, addr))

                # Temporarily set up a receiver
                original_received = None
                if hasattr(transport, "_protocol") and hasattr(
                    transport._protocol, "datagram_received"
                ):
                    original_received = transport._protocol.datagram_received
                transport._protocol.datagram_received = datagram_received

                try:
                    # Wait for data with timeout
                    data, addr = await asyncio.wait_for(
                        future, timeout=5.0
                    )  # Reduced timeout
                    data_str = data.decode("utf-8", errors="ignore")
                    loop_manager.get_loop().call_soon_threadsafe(
                        callback,
                        True,
                        data_str,
                        f"Received {len(data)} bytes from {addr[0]}:{addr[1]}",
                    )
                except asyncio.TimeoutError:
                    loop_manager.get_loop().call_soon_threadsafe(
                        callback, False, None, "UDP read timeout"
                    )
                finally:
                    # Restore original receiver if it existed
                    if original_received and hasattr(transport, "_protocol"):
                        transport._protocol.datagram_received = original_received

            except Exception as e:
                loop_manager.get_loop().call_soon_threadsafe(
                    callback, False, None, f"UDP read error: {str(e)}"
                )
            finally:
                self._decrement_operations()

        # Use create_task to properly handle the coroutine
        task = asyncio.run_coroutine_threadsafe(
            udp_read_async(), loop_manager.get_loop()
        )
        task.add_done_callback(lambda t: None)

    def udp_close(self, conn_id, callback):
        """Close UDP connection asynchronously"""
        self._increment_operations()

        async def udp_close_async():
            try:
                transport = self.udp_transports.pop(conn_id, None)
                if transport:
                    transport.close()
                    loop_manager.get_loop().call_soon_threadsafe(
                        callback, True, f"Connection {conn_id} closed"
                    )
                else:
                    loop_manager.get_loop().call_soon_threadsafe(
                        callback, False, f"Connection {conn_id} not found"
                    )
            except Exception as e:
                loop_manager.get_loop().call_soon_threadsafe(
                    callback, False, f"Close error: {str(e)}"
                )
            finally:
                self._decrement_operations()

        # Use create_task to properly handle the coroutine
        task = asyncio.run_coroutine_threadsafe(
            udp_close_async(), loop_manager.get_loop()
        )
        task.add_done_callback(lambda t: None)


# --- Global instance ---
network_manager = AsyncioNetworkManager()


# --- Utility function to check if interpreter should exit ---
@registry.register(
    description="Check if there are active network operations or callbacks",
    category="network",
)
def has_active_network_operations():
    """Check if there are any active network operations or callbacks"""
    return network_manager.has_active_operations()


# --- TCP Extension Functions ---
@registry.register(description="Connect to TCP server asynchronously", category="tcp")
def tcp_connect(host, port, callback):
    network_manager.tcp_connect(host, port, callback)


@registry.register(
    description="Write data to TCP connection asynchronously", category="tcp"
)
def tcp_write(conn_id, data, callback):
    network_manager.tcp_write(conn_id, data, callback)


@registry.register(
    description="Read data from TCP connection asynchronously", category="tcp"
)
def tcp_read(conn_id, max_bytes, callback):
    network_manager.tcp_read(conn_id, max_bytes, callback)


@registry.register(description="Close TCP connection asynchronously", category="tcp")
def tcp_close(conn_id, callback):
    network_manager.tcp_close(conn_id, callback)


# --- Synchronous TCP Extension Functions ---
@registry.register(
    description="Connect to TCP server synchronously", category="tcp_sync"
)
def tcp_connect_sync(host, port):
    """Connect to TCP server and return (success, conn_id, message)"""
    return network_manager.tcp_connect_sync(host, port)


@registry.register(
    description="Write data to TCP connection synchronously", category="tcp_sync"
)
def tcp_write_sync(conn_id, data):
    """Write data to TCP connection and return (success, bytes_written, message)"""
    return network_manager.tcp_write_sync(conn_id, data)


@registry.register(
    description="Read data from TCP connection synchronously (supports '*a', '*l', or number)",
    category="tcp_sync",
)
def tcp_read_sync(conn_id, pattern):
    """Read data from TCP connection and return (success, data, message)"""
    return network_manager.tcp_read_sync(conn_id, pattern)


@registry.register(
    description="Close TCP connection synchronously", category="tcp_sync"
)
def tcp_close_sync(conn_id):
    """Close TCP connection and return (success, message)"""
    return network_manager.tcp_close_sync(conn_id)


@registry.register(description="Set TCP timeout synchronously", category="tcp_sync")
def tcp_set_timeout_sync(conn_id, timeout_seconds):
    """Set TCP timeout for a connection and return (success, message)"""
    return network_manager.tcp_set_timeout_sync(conn_id, timeout_seconds)


@registry.register(description="Get TCP timeout synchronously", category="tcp_sync")
def tcp_get_timeout_sync(conn_id):
    """Get TCP timeout for a connection and return (success, timeout_seconds, message)"""
    return network_manager.tcp_get_timeout_sync(conn_id)


# --- UDP Extension Functions ---
@registry.register(description="Connect to UDP server asynchronously", category="udp")
def udp_connect(host, port, callback):
    network_manager.udp_connect(host, port, callback)


@registry.register(
    description="Write data to UDP connection asynchronously", category="udp"
)
def udp_write(conn_id, data, host, port, callback):
    network_manager.udp_write(conn_id, data, host, port, callback)


@registry.register(
    description="Read data from UDP connection asynchronously", category="udp"
)
def udp_read(conn_id, max_bytes, callback):
    network_manager.udp_read(conn_id, max_bytes, callback)


@registry.register(description="Close UDP connection asynchronously", category="udp")
def udp_close(conn_id, callback):
    network_manager.udp_close(conn_id, callback)


# --- Utility Functions ---
@registry.register(description="Get local IP address", category="network")
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "127.0.0.1"


@registry.register(description="Check if port is available", category="network")
def is_port_available(port, host="127.0.0.1"):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        result = s.connect_ex((host, port))
        s.close()
        return result != 0
    except Exception:
        return False


@registry.register(description="Get system hostname", category="network")
def get_hostname():
    try:
        return socket.gethostname()
    except Exception:
        return "unknown"


@registry.register(description="Set TCP timeout asynchronously", category="tcp")
def tcp_set_timeout(conn_id, timeout_seconds, callback):
    network_manager.tcp_set_timeout(conn_id, timeout_seconds, callback)


@registry.register(description="Get TCP timeout asynchronously", category="tcp")
def tcp_get_timeout(conn_id, callback):
    network_manager.tcp_get_timeout(conn_id, callback)


# HTTP request functions (LuaSocket http.request style)
def _create_http_request(
    url,
    method="GET",
    headers=None,
    body=None,
    proxy=None,
    redirect=True,
    maxredirects=5,
):
    """Create and configure HTTP request. The body must be a string if provided."""
    if headers is None:
        headers = {}

    # Add default headers if not present
    if "User-Agent" not in headers:
        headers["User-Agent"] = "PLua/1.0"

    # Create request
    if body is not None and method.upper() in ["POST", "PUT", "PATCH"]:
        if not isinstance(body, str):
            raise TypeError(
                "HTTP request body must be a string. Encode tables to JSON manually if needed."
            )
        request = urllib.request.Request(
            url, data=body.encode("utf-8"), headers=headers, method=method
        )
    else:
        request = urllib.request.Request(url, headers=headers, method=method)

    # Configure proxy if specified
    if proxy:
        proxy_handler = urllib.request.ProxyHandler({"http": proxy, "https": proxy})
        opener = urllib.request.build_opener(proxy_handler)
        urllib.request.install_opener(opener)

    return request


def _handle_http_response(response, redirect_count=0, maxredirects=5):
    """Handle HTTP response and follow redirects if needed"""
    if (
        response.getcode() in [301, 302, 303, 307, 308]
        and redirect_count < maxredirects
    ):
        location = response.headers.get("Location")
        if location:
            # Parse the new URL
            parsed_url = urlparse(response.url)
            if location.startswith("/"):
                # Relative URL
                new_url = f"{parsed_url.scheme}://{parsed_url.netloc}{location}"
            elif location.startswith("http"):
                # Absolute URL
                new_url = location
            else:
                # Relative URL without leading slash
                new_url = f"{parsed_url.scheme}://{parsed_url.netloc}/{location}"

            # Follow redirect
            return _http_request_sync(new_url, redirect_count + 1, maxredirects)

    # Always read response and return dictionary
    try:
        body_bytes = response.read()
        body = body_bytes.decode("utf-8")
    except UnicodeDecodeError:
        body = body_bytes.decode("utf-8", errors="ignore")
    except Exception:
        body = ""

    # Parse headers
    headers = {}
    for key, value in response.headers.items():
        headers[key] = value

    return {
        "code": response.getcode(),
        "headers": headers,
        "body": body,
        "url": response.url,
    }


def _http_request_sync(
    url,
    redirect_count=0,
    maxredirects=5,
    method="GET",
    headers=None,
    body=None,
    proxy=None,
    redirect=True,
):
    """Synchronous HTTP request implementation"""
    try:
        request = _create_http_request(
            url, method, headers, body, proxy, redirect, maxredirects
        )

        # Create context that ignores SSL certificate errors for development
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        with urllib.request.urlopen(request, context=context, timeout=10) as response:
            if redirect and redirect_count < maxredirects:
                return _handle_http_response(response, redirect_count, maxredirects)
            else:
                return _handle_http_response(
                    response, redirect_count, 0
                )  # No more redirects

    except urllib.error.HTTPError as e:
        # HTTP error (4xx, 5xx)
        try:
            error_body = e.read().decode("utf-8")
        except UnicodeDecodeError:
            error_body = e.read().decode("utf-8", errors="ignore")

        return {
            "code": e.code,
            "headers": dict(e.headers),
            "body": error_body,
            "url": url,
            "error": True,
        }
    except urllib.error.URLError as e:
        # Network error
        return {
            "code": 0,
            "headers": {},
            "body": "",
            "url": url,
            "error": True,
            "error_message": str(e.reason) if hasattr(e, "reason") else str(e),
        }
    except Exception as e:
        # Other errors
        return {
            "code": 0,
            "headers": {},
            "body": "",
            "url": url,
            "error": True,
            "error_message": str(e),
        }


@registry.register(
    description="Synchronous HTTP request (LuaSocket style)", category="network"
)
def http_request_sync(url_or_table):
    """
    Synchronous HTTP request function similar to LuaSocket's http.request

    Usage:
    http_request_sync("http://example.com")
    http_request_sync("http://example.com", "POST")
    http_request_sync{
    url = "http://example.com",
    method = "POST",
    headers = { ["Content-Type"] = "application/json" },
    body = "{...}",  -- Must be a string! Encode tables to JSON manually
    proxy = "http://proxy:8080",
    redirect = true,
    maxredirects = 5
    }
    Returns:
    table with: code, headers, body, url, error (optional), error_message (optional)
    """
    try:
        if isinstance(url_or_table, str):
            # Simple form: http_request_sync(url [, body])
            return _http_request_sync(url_or_table)
        elif (
            url_or_table is not None
            and hasattr(url_or_table, "values")
            and hasattr(url_or_table, "get")
        ):  # Lua table
            # Table form with parameters
            try:
                url = url_or_table["url"]
            except Exception as e:
                return {
                    "code": 0,
                    "headers": {},
                    "body": "",
                    "url": "",
                    "error": True,
                    "error_message": f"Failed to access URL: {str(e)}",
                }

            if not url:
                return {
                    "code": 0,
                    "headers": {},
                    "body": "",
                    "url": "",
                    "error": True,
                    "error_message": "URL is required",
                }

            # Extract parameters with direct access
            try:
                method = url_or_table["method"] if "method" in url_or_table else "GET"
                headers = url_or_table["headers"] if "headers" in url_or_table else {}
                body = url_or_table["body"] if "body" in url_or_table else None
                proxy = url_or_table["proxy"] if "proxy" in url_or_table else None
                redirect = (
                    url_or_table["redirect"] if "redirect" in url_or_table else True
                )
                maxredirects = (
                    url_or_table["maxredirects"]
                    if "maxredirects" in url_or_table
                    else 5
                )
            except Exception:
                # Use defaults if parameter extraction fails
                method = "GET"
                headers = {}
                body = None
                proxy = None
                redirect = True
                maxredirects = 5

            # Ensure all parameters are not None
            if headers is None:
                headers = {}
            if body is None:
                body = None  # This is fine for GET requests
            if proxy is None:
                proxy = None  # This is fine
            if redirect is None:
                redirect = True
            if maxredirects is None:
                maxredirects = 5

            return _http_request_sync(
                url, 0, maxredirects, method, headers, body, proxy, redirect
            )
        else:
            return {
                "code": 0,
                "headers": {},
                "body": "",
                "url": "",
                "error": True,
                "error_message": f"Invalid parameters: expected string or table, got {type(url_or_table)}",
            }
    except Exception as e:
        return {
            "code": 0,
            "headers": {},
            "body": "",
            "url": "",
            "error": True,
            "error_message": f"Internal error: {str(e)}",
        }


@registry.register(
    description="Asynchronous HTTP request (LuaSocket style)",
    category="network",
    inject_runtime=True,
)
def http_request_async(lua_runtime, url_or_table, callback):
    """
    Asynchronous HTTP request function similar to LuaSocket's http.request
    """
    import threading
    import queue

    def convertLuaTable(obj):
        if lupa.lua_type(obj) == "table":
            if obj[1] and not obj["_dict"]:
                b = [convertLuaTable(v) for k, v in obj.items()]
                return b
            else:
                d = dict()
                for k, v in obj.items():
                    if k != "_dict":
                        d[k] = convertLuaTable(v)
                return d
        else:
            return obj

    # Track this callback operation
    network_manager._increment_callbacks()

    # Extract data from Lua table in main thread to avoid thread safety issues
    request_data = None
    if isinstance(url_or_table, str):
        request_data = url_or_table
    elif (
        url_or_table is not None
        and hasattr(url_or_table, "values")
        and hasattr(url_or_table, "get")
    ):
        try:
            # Extract all data from Lua table in main thread
            url = url_or_table["url"]
            method = url_or_table["method"] if "method" in url_or_table else "GET"
            headers = url_or_table["headers"] if "headers" in url_or_table else {}
            body = url_or_table["body"] if "body" in url_or_table else None
            proxy = url_or_table["proxy"] if "proxy" in url_or_table else None
            redirect = url_or_table["redirect"] if "redirect" in url_or_table else True
            maxredirects = (
                url_or_table["maxredirects"] if "maxredirects" in url_or_table else 5
            )

            # Convert all Lua tables to Python objects to avoid thread safety issues
            request_data = {
                "url": convertLuaTable(url),
                "method": convertLuaTable(method),
                "headers": convertLuaTable(headers),
                "body": convertLuaTable(body),
                "proxy": convertLuaTable(proxy),
                "redirect": convertLuaTable(redirect),
                "maxredirects": convertLuaTable(maxredirects),
            }
        except Exception as e:
            # Create error response
            error_response = {
                "code": 0,
                "headers": {},
                "body": "",
                "url": "",
                "error": True,
                "error_message": f"Failed to extract request data: {str(e)}",
            }
            # Execute error callback immediately
            lua_runtime.globals()["_http_callback"] = callback
            lua_runtime.globals()["_http_response_code"] = 0
            lua_runtime.globals()["_http_response_body"] = ""
            lua_runtime.globals()["_http_response_url"] = ""
            lua_runtime.globals()["_http_response_error"] = True
            lua_runtime.globals()["_http_response_error_message"] = error_response[
                "error_message"
            ]

            callback_code = """
if _http_callback then
    local response = {
        code = _http_response_code,
        body = _http_response_body,
        url = _http_response_url,
        error = _http_response_error,
        error_message = _http_response_error_message
    }
    _http_callback(response)
end
"""
            lua_runtime.execute(callback_code)

            # Clean up globals
            for key in [
                "_http_callback",
                "_http_response_code",
                "_http_response_body",
                "_http_response_url",
                "_http_response_error",
                "_http_response_error_message",
            ]:
                if key in lua_runtime.globals():
                    del lua_runtime.globals()[key]

            # Decrement callback counter since we're done
            network_manager._decrement_callbacks()
            return

    # If we get here, we have valid request_data and should proceed with the request
    if request_data is None:
        # Handle case where neither string nor valid table was provided
        error_response = {
            "code": 0,
            "headers": {},
            "body": "",
            "url": "",
            "error": True,
            "error_message": "Invalid request parameters",
        }
        # Execute error callback immediately
        lua_runtime.globals()["_http_callback"] = callback
        lua_runtime.globals()["_http_response_code"] = 0
        lua_runtime.globals()["_http_response_body"] = ""
        lua_runtime.globals()["_http_response_url"] = ""
        lua_runtime.globals()["_http_response_error"] = True
        lua_runtime.globals()["_http_response_error_message"] = error_response[
            "error_message"
        ]

        callback_code = """
if _http_callback then
    local response = {
        code = _http_response_code,
        body = _http_response_body,
        url = _http_response_url,
        error = _http_response_error,
        error_message = _http_response_error_message
    }
    _http_callback(response)
end
"""
        lua_runtime.execute(callback_code)

        # Clean up globals
        for key in [
            "_http_callback",
            "_http_response_code",
            "_http_response_body",
            "_http_response_url",
            "_http_response_error",
            "_http_response_error_message",
        ]:
            if key in lua_runtime.globals():
                del lua_runtime.globals()[key]

        # Decrement callback counter since we're done
        network_manager._decrement_callbacks()
        return

    result_queue = queue.Queue()

    def async_request():
        try:
            response = http_request_sync(request_data)
            result_queue.put(("success", response))
        except Exception as e:
            result_queue.put(("error", str(e)))

    # Store callback in Lua globals
    lua_runtime.globals()["_http_callback"] = callback

    # Start background thread
    thread = threading.Thread(target=async_request)
    thread.daemon = False
    thread.start()
    thread.join()

    # Now, in the main thread, handle the result
    try:
        status, data = result_queue.get_nowait()
        if status == "success":
            response = data
            lua_runtime.globals()["_http_response_code"] = response["code"]
            lua_runtime.globals()["_http_response_body"] = response["body"]
            lua_runtime.globals()["_http_response_url"] = response["url"]
            lua_runtime.globals()["_http_response_error"] = response.get("error", False)
            lua_runtime.globals()["_http_response_error_message"] = response.get(
                "error_message", ""
            )
        else:
            lua_runtime.globals()["_http_response_code"] = 0
            lua_runtime.globals()["_http_response_body"] = ""
            lua_runtime.globals()["_http_response_url"] = ""
            lua_runtime.globals()["_http_response_error"] = True
            lua_runtime.globals()["_http_response_error_message"] = data

        callback_code = """
if _http_callback then
    local response = {
        code = _http_response_code,
        body = _http_response_body,
        url = _http_response_url,
        error = _http_response_error,
        error_message = _http_response_error_message
    }
    _http_callback(response)
end
"""
        lua_runtime.execute(callback_code)

        # Clean up globals
        for key in [
            "_http_response_code",
            "_http_response_body",
            "_http_response_url",
            "_http_response_error",
            "_http_response_error_message",
        ]:
            if key in lua_runtime.globals():
                del lua_runtime.globals()[key]
    except Exception:
        pass  # Silently handle any errors in callback execution
    finally:
        # Always decrement callback counter when we're done
        network_manager._decrement_callbacks()


# Alias for backward compatibility
@registry.register(
    description="HTTP request (alias for http_request_sync)", category="network"
)
def http_request(url_or_table):
    """Alias for http_request_sync for backward compatibility"""
    return http_request_sync(url_or_table)
