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
import time
import sys
import errno


# Global debug flag - will be set by the interpreter
DEBUG_MODE = False


def set_debug_mode(debug):
    """Set debug mode for network extensions"""
    global DEBUG_MODE
    DEBUG_MODE = debug


# --- Event Loop Manager ---
class AsyncioLoopManager:
    """Manages asyncio event loop in the main thread"""

    def __init__(self):
        self.loop = None

    def get_loop(self):
        if self.loop is None or self.loop.is_closed():
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
        return self.loop

    def create_task(self, coro):
        loop = self.get_loop()
        return loop.create_task(coro)

    def call_soon(self, callback, *args):
        """Schedule a callback to be called soon"""
        loop = self.get_loop()
        loop.call_soon(callback, *args)

    def run_main(self, main_coro):
        """Run the main coroutine (entry point)"""
        loop = self.get_loop()
        try:
            return loop.run_until_complete(main_coro)
        finally:
            self.shutdown()

    def shutdown(self):
        if self.loop and not self.loop.is_closed():
            try:
                # Wait a bit for any pending callbacks to complete
                time.sleep(0.1)

                pending = asyncio.all_tasks(self.loop)
                for task in pending:
                    if not task.done():
                        task.cancel()
                if pending:
                    try:
                        # Use gather instead of wait to avoid unawaited coroutine warnings
                        # Create a list of tasks to wait for
                        tasks_to_wait = [task for task in pending if not task.done()]
                        if tasks_to_wait:
                            # Use gather with return_exceptions=True to avoid unawaited coroutine warnings
                            self.loop.run_until_complete(
                                asyncio.gather(*tasks_to_wait, return_exceptions=True)
                            )
                    except Exception:
                        pass
                self.loop.close()
            except Exception:
                pass

    def stop_loop(self):
        """Stop the event loop gracefully"""
        if self.loop and not self.loop.is_closed():
            # Don't stop immediately, let the main coroutine complete naturally
            # The shutdown will be handled by the main coroutine completion
            pass

    def run_forever(self):
        """Run the event loop forever to process callbacks"""
        loop = self.get_loop()
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            self.shutdown()

    def run_until_complete(self, coro):
        """Run the event loop until the coroutine completes"""
        loop = self.get_loop()
        try:
            return loop.run_until_complete(coro)
        finally:
            self.shutdown()


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
        # Don't stop the loop here - let the main coroutine complete naturally

    def _increment_callbacks(self):
        """Increment the callback counter when starting an async operation with callback"""
        with self.lock:
            self.active_callbacks += 1

    def _decrement_callbacks(self):
        """Decrement the callback counter when a callback completes"""
        with self.lock:
            self.active_callbacks -= 1
        # Don't stop the loop here - let the main coroutine complete naturally

    def has_active_operations(self):
        """Check if there are any active network operations or callbacks"""
        with self.lock:
            # Only consider it active if there are actual operations, connections, or callbacks
            # Don't count just the event loop being running as an active operation
            has_actual_operations = (
                self.active_operations > 0
                or len(self.tcp_connections) > 0
                or len(self.udp_transports) > 0
                or self.active_callbacks > 0
            )

            return has_actual_operations

    def force_cleanup(self):
        """Force cleanup of all operations and connections"""
        with self.lock:
            # Close all TCP connections
            for conn_id in list(self.tcp_connections.keys()):
                try:
                    reader, writer = self.tcp_connections[conn_id]
                    if writer:
                        if hasattr(writer, 'close'):
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

    def _notify_server_client_disconnect(self, conn_id):
        """Notify TCP servers when a client disconnects"""
        # Check if this connection belongs to any TCP server
        for server in tcp_server_manager.servers.values():
            if conn_id in server.clients:
                if DEBUG_MODE:
                    print(f"[DEBUG] AsyncioNetworkManager._notify_server_client_disconnect: Notifying server {server.server_id} about client {conn_id} disconnect")
                # Get the writer from the server's clients dict
                reader, writer = server.clients.get(conn_id, (None, None))
                if writer:
                    server._handle_client_disconnect(conn_id, writer)
                break

    # --- TCP ---
    def tcp_connect(self, host, port, callback):
        """Connect to TCP server using asyncio (consistent with TCP server)"""
        self._increment_operations()
        self._increment_callbacks()

        # Generate a unique callback ID for this operation
        callback_id = self._next_conn_id()

        # Store the callback in Lua (similar to timer callbacks)
        try:
            from plua.coroutine_manager import coroutine_manager_instance
            if coroutine_manager_instance:
                # Store the callback in Lua's network callback system
                coroutine_manager_instance.lua_runtime.globals()["__temp_network_callback"] = callback
                coroutine_manager_instance.lua_runtime.execute(f"_PY.net_callbacks[{callback_id}] = __temp_network_callback")
                coroutine_manager_instance.lua_runtime.globals()["__temp_network_callback"] = None
        except Exception as e:
            print(f"[DEBUG] Failed to store network callback: {e}")
            self._decrement_operations()
            self._decrement_callbacks()
            return

        async def tcp_connect_async():
            try:
                # Use asyncio to create the connection
                reader, writer = await asyncio.open_connection(host, port)

                # Store connection with a unique ID
                conn_id = self._next_conn_id()
                self.tcp_connections[conn_id] = (reader, writer)

                # Queue callback through coroutine manager with parameters
                from plua.coroutine_manager import queue_callback_with_params
                queue_callback_with_params(callback_id, True, conn_id, f"Connected to {host}:{port}")

            except Exception as e:
                # Queue callback through coroutine manager with parameters
                from plua.coroutine_manager import queue_callback_with_params
                queue_callback_with_params(callback_id, False, None, f"TCP connect error: {str(e)}")
            finally:
                self._decrement_operations()
                self._decrement_callbacks()

        # Create task on the main thread event loop
        task = loop_manager.create_task(tcp_connect_async())
        task.add_done_callback(lambda t: None)

    async def tcp_write_async(self, conn_id, data, callback_id):
        """Write data to TCP connection asynchronously"""
        try:
            reader, writer = self.tcp_connections.get(conn_id, (None, None))
            if not writer:
                from plua.coroutine_manager import queue_callback_with_params
                queue_callback_with_params(callback_id, False, None, f"TCP connection {conn_id} not found")
                return

            if isinstance(data, str):
                data_bytes = data.encode("utf-8")
            else:
                data_bytes = bytes(data)

            writer.write(data_bytes)
            await writer.drain()

            # Only queue the parameterized callback
            from plua.coroutine_manager import queue_callback_with_params
            queue_callback_with_params(callback_id, True, len(data_bytes), f"Sent {len(data_bytes)} bytes")
        except Exception as e:
            from plua.coroutine_manager import queue_callback_with_params
            queue_callback_with_params(callback_id, False, None, f"TCP write error: {str(e)}")
        finally:
            self._decrement_operations()
            self._decrement_callbacks()

    def tcp_write(self, conn_id, data, callback):
        """Write data to TCP connection asynchronously"""
        self._increment_operations()
        self._increment_callbacks()

        # Generate a unique callback ID for this operation
        callback_id = self._next_conn_id()

        # Store the callback in Lua (similar to timer callbacks)
        try:
            from plua.coroutine_manager import coroutine_manager_instance
            if coroutine_manager_instance:
                # Store the callback in Lua's network callback system
                coroutine_manager_instance.lua_runtime.globals()["__temp_network_callback"] = callback
                coroutine_manager_instance.lua_runtime.execute(f"_PY.net_callbacks[{callback_id}] = __temp_network_callback")
                coroutine_manager_instance.lua_runtime.globals()["__temp_network_callback"] = None
        except Exception as e:
            print(f"[DEBUG] Failed to store network callback: {e}")
            self._decrement_operations()
            self._decrement_callbacks()
            return

        # Create task on the main thread event loop
        task = loop_manager.create_task(self.tcp_write_async(conn_id, data, callback_id))
        task.add_done_callback(lambda t: None)

    async def tcp_read_async(self, conn_id, max_bytes, callback_id):
        """Read data from TCP connection asynchronously"""
        try:
            reader, writer = self.tcp_connections.get(conn_id, (None, None))
            if not reader:
                from plua.coroutine_manager import queue_callback_with_params
                queue_callback_with_params(callback_id, False, None, f"TCP connection {conn_id} not found")
                return

            try:
                data = await asyncio.wait_for(reader.read(max_bytes), timeout=5.0)
                if data:
                    data_str = data.decode("utf-8", errors="ignore")
                    from plua.coroutine_manager import queue_callback_with_params
                    queue_callback_with_params(callback_id, True, data_str, f"Received {len(data)} bytes")
                else:
                    from plua.coroutine_manager import queue_callback_with_params
                    queue_callback_with_params(callback_id, False, None, "Connection closed by peer")
                    self.tcp_connections.pop(conn_id, None)
                    self._notify_server_client_disconnect(conn_id)
            except asyncio.TimeoutError:
                from plua.coroutine_manager import queue_callback_with_params
                queue_callback_with_params(callback_id, False, None, "Read timeout")
        except Exception as e:
            from plua.coroutine_manager import queue_callback_with_params
            queue_callback_with_params(callback_id, False, None, f"Read error: {str(e)}")
        finally:
            self._decrement_operations()
            self._decrement_callbacks()

    def tcp_read(self, conn_id, max_bytes, callback):
        """Read data from TCP connection asynchronously"""
        self._increment_operations()
        self._increment_callbacks()

        # Generate a unique callback ID for this operation
        callback_id = self._next_conn_id()

        # Store the callback in Lua (similar to timer callbacks)
        try:
            from plua.coroutine_manager import coroutine_manager_instance
            if coroutine_manager_instance:
                # Store the callback in Lua's network callback system
                coroutine_manager_instance.lua_runtime.globals()["__temp_network_callback"] = callback
                coroutine_manager_instance.lua_runtime.execute(f"_PY.net_callbacks[{callback_id}] = __temp_network_callback")
                coroutine_manager_instance.lua_runtime.globals()["__temp_network_callback"] = None
        except Exception as e:
            print(f"[DEBUG] Failed to store network callback: {e}")
            self._decrement_operations()
            self._decrement_callbacks()
            return

        # Create task on the main thread event loop
        task = loop_manager.create_task(self.tcp_read_async(conn_id, max_bytes, callback_id))
        task.add_done_callback(lambda t: None)

    async def tcp_close_async(self, conn_id, callback_id):
        try:
            reader, writer = self.tcp_connections.pop(conn_id, (None, None))
            if writer:
                if hasattr(writer, 'close') and hasattr(writer, 'wait_closed'):
                    writer.close()
                    await writer.wait_closed()
                else:
                    sock = writer
                    sock.close()
                from plua.coroutine_manager import queue_callback_with_params
                queue_callback_with_params(callback_id, True, f"Connection {conn_id} closed")
            else:
                from plua.coroutine_manager import queue_callback_with_params
                queue_callback_with_params(callback_id, False, f"Connection {conn_id} not found")
        except Exception as e:
            from plua.coroutine_manager import queue_callback_with_params
            queue_callback_with_params(callback_id, False, f"Close error: {str(e)}")
        finally:
            self._decrement_operations()
            self._decrement_callbacks()

    def tcp_close(self, conn_id, callback):
        """Close TCP connection asynchronously"""
        self._increment_operations()
        self._increment_callbacks()

        # Generate a unique callback ID for this operation
        callback_id = self._next_conn_id()

        # Store the callback in Lua (similar to timer callbacks)
        try:
            from plua.coroutine_manager import coroutine_manager_instance
            if coroutine_manager_instance:
                # Store the callback in Lua's network callback system
                coroutine_manager_instance.lua_runtime.globals()["__temp_network_callback"] = callback
                coroutine_manager_instance.lua_runtime.execute(f"_PY.net_callbacks[{callback_id}] = __temp_network_callback")
                coroutine_manager_instance.lua_runtime.globals()["__temp_network_callback"] = None
        except Exception as e:
            print(f"[DEBUG] Failed to store network callback: {e}")
            self._decrement_operations()
            self._decrement_callbacks()
            return

        # Create task on the main thread event loop
        task = loop_manager.create_task(self.tcp_close_async(conn_id, callback_id))
        task.add_done_callback(lambda t: None)

    # --- Synchronous TCP Functions ---
    def tcp_connect_sync(self, host, port):
        """Synchronous TCP connect - returns (success, conn_id, message)"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)  # 1 second timeout instead of 10
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
                    # Notify TCP server if this is a server client connection
                    self._notify_server_client_disconnect(conn_id)
                    return False, None, "Connection closed by peer"

            elif pattern == "*l":
                # Read a line (terminated by LF, CR ignored)
                line_parts = []
                while True:
                    char = sock.recv(1)
                    if not char:
                        # Connection closed
                        self.tcp_connections.pop(conn_id, None)
                        # Notify TCP server if this is a server client connection
                        self._notify_server_client_disconnect(conn_id)
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
                    # Notify TCP server if this is a server client connection
                    self._notify_server_client_disconnect(conn_id)
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
            if e.errno == errno.EAGAIN or e.errno == errno.EWOULDBLOCK:
                # No data available, but connection is still open
                return False, None, "No data available (would block)"
            else:
                # Other BlockingIOError, remove connection
                self.tcp_connections.pop(conn_id, None)
                # Notify TCP server if this is a server client connection
                self._notify_server_client_disconnect(conn_id)
                return False, None, f"TCP read error: {str(e)}"
        except ConnectionError as e:
            # Remove connection for actual connection errors
            self.tcp_connections.pop(conn_id, None)
            # Notify TCP server if this is a server client connection
            self._notify_server_client_disconnect(conn_id)
            return False, None, f"TCP connection error: {str(e)}"
        except Exception as e:
            # Remove connection for other unexpected errors
            self.tcp_connections.pop(conn_id, None)
            # Notify TCP server if this is a server client connection
            self._notify_server_client_disconnect(conn_id)
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

    def tcp_read_until_sync(self, conn_id, delimiter, max_bytes=8192):
        """Read data from TCP connection until delimiter is found - returns (success, data, message)"""
        try:
            reader, writer = self.tcp_connections.get(conn_id, (None, None))
            if not reader:
                return False, None, f"TCP connection {conn_id} not found"

            sock = reader
            data_parts = []
            total_bytes = 0
            delimiter_bytes = delimiter.encode('utf-8')

            while total_bytes < max_bytes:
                # Read one byte at a time to check for delimiter
                chunk = sock.recv(1)
                if not chunk:
                    # Connection closed by peer
                    self.tcp_connections.pop(conn_id, None)
                    # Notify TCP server if this is a server client connection
                    self._notify_server_client_disconnect(conn_id)
                    if data_parts:
                        data = b"".join(data_parts)
                        data_str = data.decode("utf-8", errors="ignore")
                        return True, data_str, f"Received {len(data)} bytes (connection closed)"
                    else:
                        return False, None, "Connection closed by peer"

                data_parts.append(chunk)
                total_bytes += 1

                # Check if we have enough data to form the delimiter
                if len(data_parts) >= len(delimiter_bytes):
                    # Check if the last bytes match the delimiter
                    recent_data = b"".join(data_parts[-len(delimiter_bytes):])
                    if recent_data == delimiter_bytes:
                        # Found delimiter, return data including delimiter
                        data = b"".join(data_parts)
                        data_str = data.decode("utf-8", errors="ignore")
                        return True, data_str, f"Received {len(data)} bytes (delimiter found)"

            # Max bytes reached without finding delimiter
            data = b"".join(data_parts)
            data_str = data.decode("utf-8", errors="ignore")
            return True, data_str, f"Received {len(data)} bytes (max bytes reached)"

        except socket.timeout:
            # Don't remove connection for timeout errors (including non-blocking)
            return True, "", "No data available (non-blocking socket)"
        except BlockingIOError as e:
            if e.errno == errno.EAGAIN or e.errno == errno.EWOULDBLOCK:
                # No data available, but connection is still open
                return True, "", "No data available (would block)"
            else:
                # Other BlockingIOError, remove connection
                self.tcp_connections.pop(conn_id, None)
                # Notify TCP server if this is a server client connection
                self._notify_server_client_disconnect(conn_id)
                return False, None, f"TCP read error: {str(e)}"
        except ConnectionError as e:
            # Remove connection for actual connection errors
            self.tcp_connections.pop(conn_id, None)
            # Notify TCP server if this is a server client connection
            self._notify_server_client_disconnect(conn_id)
            return False, None, f"TCP connection error: {str(e)}"
        except Exception as e:
            # Remove connection for other unexpected errors
            self.tcp_connections.pop(conn_id, None)
            # Notify TCP server if this is a server client connection
            self._notify_server_client_disconnect(conn_id)
            return False, None, f"TCP read error: {str(e)}"

    # --- Asynchronous TCP Timeout Functions ---
    async def tcp_set_timeout_async(self, conn_id, timeout_seconds, callback):
        self._increment_operations()
        self._increment_callbacks()
        try:
            reader, writer = self.tcp_connections.get(conn_id, (None, None))
            if not reader or not writer:
                loop_manager.call_soon(
                    callback, False, f"TCP connection {conn_id} not found"
                )
                return

            # Both reader and writer are the same socket object
            sock = reader
            sock.settimeout(timeout_seconds)

            if timeout_seconds is None:
                loop_manager.call_soon(
                    callback,
                    True,
                    f"Socket set to blocking mode for connection {conn_id}",
                )
            elif timeout_seconds == 0:
                loop_manager.call_soon(
                    callback,
                    True,
                    f"Socket set to non-blocking mode for connection {conn_id}",
                )
            else:
                loop_manager.call_soon(
                    callback,
                    True,
                    f"Timeout set to {timeout_seconds} seconds for connection {conn_id}",
                )

        except Exception as e:
            loop_manager.call_soon(
                callback, False, f"TCP timeout set error: {str(e)}"
            )
        finally:
            self._decrement_operations()
            self._decrement_callbacks()

    def tcp_set_timeout(self, conn_id, timeout_seconds, callback):
        """Asynchronous TCP timeout setter"""
        task = loop_manager.create_task(
            self.tcp_set_timeout_async(conn_id, timeout_seconds, callback)
        )
        task.add_done_callback(lambda t: None)

    async def tcp_get_timeout_async(self, conn_id, callback):
        self._increment_operations()
        self._increment_callbacks()
        try:
            reader, writer = self.tcp_connections.get(conn_id, (None, None))
            if not reader or not writer:
                loop_manager.call_soon(
                    callback, False, None, f"TCP connection {conn_id} not found"
                )
                return

            # Both reader and writer are the same socket object
            sock = reader
            timeout = sock.gettimeout()

            if timeout is None:
                loop_manager.call_soon(
                    callback,
                    True,
                    timeout,
                    f"Socket is in blocking mode for connection {conn_id}",
                )
            elif timeout == 0:
                loop_manager.call_soon(
                    callback,
                    True,
                    timeout,
                    f"Socket is in non-blocking mode for connection {conn_id}",
                )
            else:
                loop_manager.call_soon(
                    callback,
                    True,
                    timeout,
                    f"Current timeout: {timeout} seconds for connection {conn_id}",
                )

        except Exception as e:
            loop_manager.call_soon(
                callback, False, None, f"TCP timeout get error: {str(e)}"
            )
        finally:
            self._decrement_operations()
            self._decrement_callbacks()

    def tcp_get_timeout(self, conn_id, callback):
        """Asynchronous TCP timeout getter"""
        task = loop_manager.create_task(
            self.tcp_get_timeout_async(conn_id, callback)
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
            loop_manager.call_soon(
                self.callback,
                True,
                self.conn_id,
                f"UDP connected (conn_id={self.conn_id})",
            )

        def datagram_received(self, data, addr):
            # Not used in this demo, but could be extended
            pass

        def error_received(self, exc):
            loop_manager.call_soon(
                self.callback, False, self.conn_id, f"UDP error: {exc}"
            )

        def connection_lost(self, exc):
            self.manager.udp_transports.pop(self.conn_id, None)

    def udp_connect(self, host, port, callback):
        """Connect to UDP server asynchronously"""
        self._increment_operations()
        self._increment_callbacks()

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
                loop_manager.call_soon(
                    callback, False, None, f"UDP connect error: {str(e)}"
                )
            finally:
                self._decrement_operations()
                self._decrement_callbacks()

        # Create task on the main thread event loop
        task = loop_manager.create_task(udp_connect_async())
        task.add_done_callback(lambda t: None)

    def udp_write(self, conn_id, data, host, port, callback):
        """Write data to UDP connection asynchronously"""
        self._increment_operations()
        self._increment_callbacks()

        async def udp_write_async():
            try:
                transport = self.udp_transports.get(conn_id)
                if not transport:
                    loop_manager.call_soon(
                        callback, False, None, f"UDP connection {conn_id} not found"
                    )
                    return
                if isinstance(data, str):
                    data_bytes = data.encode("utf-8")
                else:
                    data_bytes = bytes(data)
                transport.sendto(data_bytes, (host, port))
                loop_manager.call_soon(
                    callback,
                    True,
                    len(data_bytes),
                    f"Sent {len(data_bytes)} bytes to {host}:{port}",
                )
            except Exception as e:
                loop_manager.call_soon(
                    callback, False, None, f"UDP write error: {str(e)}"
                )
            finally:
                self._decrement_operations()
                self._decrement_callbacks()

        # Create task on the main thread event loop
        task = loop_manager.create_task(udp_write_async())
        task.add_done_callback(lambda t: None)

    def udp_read(self, conn_id, max_bytes, callback):
        """Read data from UDP connection asynchronously"""
        self._increment_operations()
        self._increment_callbacks()

        async def udp_read_async():
            try:
                transport = self.udp_transports.get(conn_id)
                if not transport:
                    loop_manager.call_soon(
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
                    loop_manager.call_soon(
                        callback,
                        True,
                        data_str,
                        f"Received {len(data)} bytes from {addr[0]}:{addr[1]}",
                    )
                except asyncio.TimeoutError:
                    loop_manager.call_soon(
                        callback, False, None, "UDP read timeout"
                    )
                finally:
                    # Restore original receiver if it existed
                    if original_received and hasattr(transport, "_protocol"):
                        transport._protocol.datagram_received = original_received

            except Exception as e:
                loop_manager.call_soon(
                    callback, False, None, f"UDP read error: {str(e)}"
                )
            finally:
                self._decrement_operations()
                self._decrement_callbacks()

        # Create task on the main thread event loop
        task = loop_manager.create_task(udp_read_async())
        task.add_done_callback(lambda t: None)

    def udp_close(self, conn_id, callback):
        """Close UDP connection asynchronously"""
        self._increment_operations()
        self._increment_callbacks()

        async def udp_close_async():
            try:
                transport = self.udp_transports.pop(conn_id, None)
                if transport:
                    transport.close()
                    loop_manager.call_soon(
                        callback, True, f"Connection {conn_id} closed"
                    )
                else:
                    loop_manager.call_soon(
                        callback, False, f"Connection {conn_id} not found"
                    )
            except Exception as e:
                loop_manager.call_soon(
                    callback, False, f"Close error: {str(e)}"
                )
            finally:
                self._decrement_operations()
                self._decrement_callbacks()

        # Create task on the main thread event loop
        task = loop_manager.create_task(udp_close_async())
        task.add_done_callback(lambda t: None)

    async def tcp_read_until_async(self, conn_id, delimiter, max_bytes, callback):
        self._increment_operations()
        self._increment_callbacks()
        try:
            reader, writer = self.tcp_connections.get(conn_id, (None, None))
            if not reader:
                loop_manager.call_soon(
                    callback, False, None, f"TCP connection {conn_id} not found"
                )
                return

            data_parts = []
            total_bytes = 0
            delimiter_bytes = delimiter.encode('utf-8')

            # Check if this is an asyncio StreamReader (from tcp_connect or tcp_server) or socket object (from tcp_connect_sync)
            if hasattr(reader, 'read'):
                # This is an asyncio StreamReader (from tcp_connect or tcp_server)
                while total_bytes < max_bytes:
                    # Read one byte at a time to check for delimiter
                    chunk = await reader.read(1)
                    if not chunk:
                        # Connection closed by peer
                        self.tcp_connections.pop(conn_id, None)
                        # Notify TCP server if this is a server client connection
                        self._notify_server_client_disconnect(conn_id)
                        if data_parts:
                            data = b"".join(data_parts)
                            data_str = data.decode("utf-8", errors="ignore")
                            loop_manager.call_soon(
                                callback, True, data_str, f"Received {len(data)} bytes (connection closed)"
                            )
                        else:
                            loop_manager.call_soon(
                                callback, False, None, "Connection closed by peer"
                            )
                        return

                    data_parts.append(chunk)
                    total_bytes += 1

                    # Check if we have enough data to form the delimiter
                    if len(data_parts) >= len(delimiter_bytes):
                        # Check if the last bytes match the delimiter
                        recent_data = b"".join(data_parts[-len(delimiter_bytes):])
                        if recent_data == delimiter_bytes:
                            # Found delimiter, return data including delimiter
                            data = b"".join(data_parts)
                            data_str = data.decode("utf-8", errors="ignore")
                            loop_manager.call_soon(
                                callback, True, data_str, f"Received {len(data)} bytes (delimiter found)"
                            )
                            return

                # Max bytes reached without finding delimiter
                data = b"".join(data_parts)
                data_str = data.decode("utf-8", errors="ignore")
                loop_manager.call_soon(
                    callback, True, data_str, f"Received {len(data)} bytes (max bytes reached)"
                )
            else:
                # This is a socket object (from tcp_connect_sync)
                sock = reader  # reader is actually a socket object
                # Set a short timeout for the read operation
                sock.settimeout(2)  # 2 second timeout for read operations

                try:
                    while total_bytes < max_bytes:
                        # Read one byte at a time to check for delimiter
                        chunk = sock.recv(1)
                        if not chunk:
                            # Connection closed by peer
                            self.tcp_connections.pop(conn_id, None)
                            # Notify TCP server if this is a server client connection
                            self._notify_server_client_disconnect(conn_id)
                            if data_parts:
                                data = b"".join(data_parts)
                                data_str = data.decode("utf-8", errors="ignore")
                                loop_manager.call_soon(
                                    callback, True, data_str, f"Received {len(data)} bytes (connection closed)"
                                )
                            else:
                                loop_manager.call_soon(
                                    callback, False, None, "Connection closed by peer"
                                )
                            return

                        data_parts.append(chunk)
                        total_bytes += 1

                        # Check if we have enough data to form the delimiter
                        if len(data_parts) >= len(delimiter_bytes):
                            # Check if the last bytes match the delimiter
                            recent_data = b"".join(data_parts[-len(delimiter_bytes):])
                            if recent_data == delimiter_bytes:
                                # Found delimiter, return data including delimiter
                                data = b"".join(data_parts)
                                data_str = data.decode("utf-8", errors="ignore")
                                loop_manager.call_soon(
                                    callback, True, data_str, f"Received {len(data)} bytes (delimiter found)"
                                )
                                return

                    # Max bytes reached without finding delimiter
                    data = b"".join(data_parts)
                    data_str = data.decode("utf-8", errors="ignore")
                    loop_manager.call_soon(
                        callback, True, data_str, f"Received {len(data)} bytes (max bytes reached)"
                    )
                except socket.timeout:
                    loop_manager.call_soon(
                        callback, False, None, "TCP read timeout"
                    )
                    return

        except Exception as e:
            loop_manager.call_soon(
                callback, False, None, f"TCP read until error: {str(e)}"
            )
        finally:
            self._decrement_operations()
            self._decrement_callbacks()

    def tcp_read_until(self, conn_id, delimiter, max_bytes, callback):
        # Create task on the main thread event loop
        task = loop_manager.create_task(
            self.tcp_read_until_async(conn_id, delimiter, max_bytes, callback)
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


@registry.register(description="Read data from TCP connection until delimiter is found", category="tcp_sync")
def tcp_read_until_sync(conn_id, delimiter, max_bytes=8192):
    """Read data from TCP connection until delimiter is found - returns (success, data, message)"""
    return network_manager.tcp_read_until_sync(conn_id, delimiter, max_bytes)


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


def _http_request_sync_legacy(
    url,
    redirect_count=0,
    maxredirects=5,
    method="GET",
    headers=None,
    body=None,
    proxy=None,
    redirect=True,
):
    """Legacy synchronous HTTP request implementation using urllib"""
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
    """Synchronous HTTP request implementation using asyncio and httpx"""

    # Always use legacy implementation to avoid hanging issues
    # The httpx/asyncio threading approach seems to have issues
    return _http_request_sync_legacy(
        url, redirect_count, maxredirects, method, headers, body, proxy, redirect
    )


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
            # Execute the callback directly
            try:
                lua_runtime.execute(callback_code)
            except Exception as e:
                print(f"Error executing HTTP callback: {e}", file=sys.stderr)
            finally:
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
        # Execute the callback directly
        try:
            lua_runtime.execute(callback_code)
        except Exception as e:
            print(f"Error executing HTTP callback: {e}", file=sys.stderr)
        finally:
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
        # Execute the callback directly
        try:
            lua_runtime.execute(callback_code)
        except Exception as e:
            print(f"Error executing HTTP callback: {e}", file=sys.stderr)
        finally:
            network_manager._decrement_callbacks()
    except Exception as e:
        print(f"Error in HTTP request processing: {e}", file=sys.stderr)
        network_manager._decrement_callbacks()


# Alias for backward compatibility
@registry.register(
    description="HTTP request (alias for http_request_sync)", category="network"
)
def http_request(url_or_table):
    """Alias for http_request_sync for backward compatibility"""
    return http_request_sync(url_or_table)


@registry.register(
    description="Read data from TCP connection until delimiter asynchronously", category="tcp"
)
def tcp_read_until(conn_id, delimiter, max_bytes, callback):
    network_manager.tcp_read_until(conn_id, delimiter, max_bytes, callback)


# --- TCP Server Extensions ---
class TCPServerManager:
    def __init__(self):
        self.servers = {}  # server_id: TCPServer
        self.next_id = 1
        self.lock = threading.Lock()
        self.active_operations = 0
        self.active_callbacks = 0

    def _next_server_id(self):
        with self.lock:
            sid = self.next_id
            self.next_id += 1
            return sid

    def _increment_operations(self):
        with self.lock:
            self.active_operations += 1

    def _decrement_operations(self):
        with self.lock:
            self.active_operations -= 1

    def _increment_callbacks(self):
        with self.lock:
            self.active_callbacks += 1

    def _decrement_callbacks(self):
        with self.lock:
            self.active_callbacks -= 1

    def has_active_operations(self):
        with self.lock:
            return self.active_operations > 0 or len(self.servers) > 0 or self.active_callbacks > 0

    def force_cleanup(self):
        with self.lock:
            for server_id in list(self.servers.keys()):
                try:
                    server = self.servers[server_id]
                    if server:
                        server.close()
                except Exception:
                    pass
            self.servers.clear()
            self.active_operations = 0
            self.active_callbacks = 0


class TCPServer:
    def __init__(self, server_id, manager):
        self.server_id = server_id
        self.manager = manager
        self.server = None
        self.clients = {}  # client_id: (reader, writer)
        self.next_client_id = 10000  # Start from 10000 to avoid conflicts with network manager
        self.event_listeners = {
            'client_connected': [],
            'client_disconnected': [],
            'error': []
        }
        self.running = False
        self.ready = False  # Track if server is ready to accept connections

    def add_event_listener(self, event_name, callback):
        if DEBUG_MODE:
            cb_info = f"{callback}, id={id(callback)}, type={type(callback)}, repr={repr(callback)}"
            print(f"[DEBUG] TCPServer._emit_event: Calling callback {len(self.event_listeners[event_name])+1}/{len(self.event_listeners[event_name])}: {cb_info}")
        if event_name in self.event_listeners:
            self.event_listeners[event_name].append(callback)
            if DEBUG_MODE:
                print(f"[DEBUG] TCPServer.add_event_listener: Added callback. Total listeners for {event_name}: {len(self.event_listeners[event_name])}")
                listeners_repr = [repr(cb) + ' id=' + str(id(cb)) for cb in self.event_listeners[event_name]]
                print(f"[DEBUG] TCPServer._emit_event: Listener list for {event_name}: {listeners_repr}")
        else:
            if DEBUG_MODE:
                print(f"[DEBUG] TCPServer.add_event_listener: Unknown event '{event_name}'")

    def start(self, host, port):
        """Start the TCP server"""
        if self.running:
            if DEBUG_MODE:
                print(f"[DEBUG] TCPServer.start: Server {self.server_id} is already running")
            return

        if DEBUG_MODE:
            print(f"[DEBUG] TCPServer.start: Starting server {self.server_id} on {host}:{port}")

        async def start_server():
            try:
                self.server = await asyncio.start_server(
                    self._handle_client, host, port
                )
                self.running = True
                self.ready = True  # Server is now ready to accept connections
                if DEBUG_MODE:
                    print(f"[DEBUG] TCPServer.start: Server {self.server_id} started successfully on {host}:{port}")

                # Keep the server running
                async with self.server:
                    await self.server.serve_forever()

            except Exception as e:
                if DEBUG_MODE:
                    print(f"[DEBUG] TCPServer.start: Error starting server {self.server_id}: {e}")
                self._emit_event('error', str(e))

        # Start the server in a separate task and ensure event loop is running
        task = loop_manager.create_task(start_server())
        task.add_done_callback(lambda t: None)

        # Start event loop in background if not already running
        def start_event_loop():
            try:
                loop = loop_manager.get_loop()
                if not loop.is_running():
                    loop.run_forever()
            except Exception as e:
                if DEBUG_MODE:
                    print(f"[DEBUG] TCPServer.start: Event loop error: {e}")

        # Start event loop in background thread
        import threading
        event_loop_thread = threading.Thread(target=start_event_loop, daemon=True)
        event_loop_thread.start()

    def is_ready(self):
        """Check if the server is ready to accept connections"""
        return self.ready and self.running

    def _handle_client(self, reader, writer):
        """Handle a new client connection"""
        client_id = self.next_client_id
        self.next_client_id += 1

        addr = writer.get_extra_info('peername')
        if DEBUG_MODE:
            print(f"[DEBUG] TCPServer._handle_client: New client {client_id} connected from {addr}")

        # Store the client connection in the server's clients dict
        self.clients[client_id] = (reader, writer)

        # Also register the client with the network manager so tcp_write/tcp_read can find it
        network_manager.tcp_connections[client_id] = (reader, writer)

        # Emit client_connected event
        self._emit_event('client_connected', client_id, addr)

        # Note: We don't start the automatic read loop here to avoid conflicts with manual reads
        # The Lua code can use tcp_read() to read data manually

    def _handle_client_disconnect(self, client_id, writer):
        """Handle client disconnection"""
        addr = writer.get_extra_info('peername')
        if DEBUG_MODE:
            print(f"[DEBUG] TCPServer._handle_client_disconnect: Client {client_id} disconnected from {addr}")

        # Remove from clients dict
        self.clients.pop(client_id, None)

        # Also remove from network manager
        network_manager.tcp_connections.pop(client_id, None)

        # Close the connection
        writer.close()
        try:
            # Note: We can't await here since this is not async
            # The connection will be closed when the event loop processes it
            pass
        except Exception:
            pass

        # Emit client_disconnected event
        self._emit_event('client_disconnected', client_id, addr)

    def _emit_event(self, event_name, *args):
        """Emit an event to all registered listeners"""
        if event_name not in self.event_listeners:
            if DEBUG_MODE:
                print(f"[DEBUG] TCPServer._emit_event: Unknown event '{event_name}'")
            return

        listeners = self.event_listeners[event_name]
        if DEBUG_MODE:
            print(f"[DEBUG] TCPServer._emit_event: Emitting '{event_name}' to {len(listeners)} listeners")

        for i, callback in enumerate(listeners):
            try:
                if DEBUG_MODE:
                    cb_info = f"{callback}, id={id(callback)}, type={type(callback)}, repr={repr(callback)}"
                    print(f"[DEBUG] TCPServer._emit_event: Calling callback {i+1}/{len(listeners)}: {cb_info}")

                # Schedule the callback to run on the main thread
                loop_manager.call_soon(callback, *args)

            except Exception as e:
                if DEBUG_MODE:
                    print(f"[DEBUG] TCPServer._emit_event: Error in {event_name} callback: {e}")

    def close(self):
        """Close the TCP server and all client connections"""
        if not self.running:
            return

        if DEBUG_MODE:
            print(f"[DEBUG] TCPServer.close: Closing server {self.server_id}")

        # Close all client connections
        for client_id in list(self.clients.keys()):
            try:
                reader, writer = self.clients[client_id]
                writer.close()
                # Also remove from network manager
                network_manager.tcp_connections.pop(client_id, None)
            except Exception:
                pass
        self.clients.clear()

        # Close the server
        if self.server:
            self.server.close()

        self.running = False
        if DEBUG_MODE:
            print(f"[DEBUG] TCPServer.close: Server {self.server_id} closed")


# Global TCP server manager instance
tcp_server_manager = TCPServerManager()


@registry.register(description="Create TCP server", category="tcp_server")
def tcp_server_create():
    server_id = tcp_server_manager._next_server_id()
    server = TCPServer(server_id, tcp_server_manager)
    tcp_server_manager.servers[server_id] = server
    return server_id


@registry.register(description="Add event listener to TCP server", category="tcp_server")
def tcp_server_add_event_listener(server_id, event_name, callback):
    if DEBUG_MODE:
        print(f"[DEBUG] tcp_server_add_event_listener: server_id={server_id}, event_name={event_name}, callback={callback}")
    server = tcp_server_manager.servers.get(server_id)
    if server:
        if DEBUG_MODE:
            print(f"[DEBUG] tcp_server_add_event_listener: Found server {server_id}, adding listener")
        server.add_event_listener(event_name, callback)
    else:
        if DEBUG_MODE:
            print(f"[DEBUG] tcp_server_add_event_listener: Server {server_id} not found!")


@registry.register(description="Start TCP server", category="tcp_server")
def tcp_server_start(server_id, host, port):
    server = tcp_server_manager.servers.get(server_id)
    if server:
        server.start(host, port)


@registry.register(description="Check if TCP server is ready", category="tcp_server")
def tcp_server_is_ready(server_id):
    server = tcp_server_manager.servers.get(server_id)
    if server:
        return server.is_ready()
    return False


@registry.register(description="Close TCP server", category="tcp_server")
def tcp_server_close(server_id):
    server = tcp_server_manager.servers.get(server_id)
    if server:
        server.close()


@registry.register(description="Check if there are active TCP server operations", category="tcp_server")
def has_active_tcp_server_operations():
    return tcp_server_manager.has_active_operations()


# --- Synchronous API Manager for External System Communication ---
class SynchronousAPIManager:
    """Manages synchronous API calls using traditional socket server"""

    def __init__(self):
        self.pending_requests = {}  # request_id: (event, result_holder)
        self.next_request_id = 1
        self.lock = threading.Lock()
        self.server_socket = None
        self.client_socket = None
        self.server_thread = None
        self.running = False

    def _next_request_id(self):
        with self.lock:
            rid = self.next_request_id
            self.next_request_id += 1
            return rid

    def setup_tcp_server(self, host, port):
        """Setup traditional TCP server for external system connections"""
        import socket

        try:
            # Create a traditional socket server
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((host, port))
            self.server_socket.listen(1)
            self.server_socket.settimeout(0.1)  # Non-blocking accept
            self.running = True

            # Start server thread
            self.server_thread = threading.Thread(target=self._server_loop, daemon=True)
            self.server_thread.start()

            print(f"[SYNC API] Traditional socket server started on {host}:{port}")
            return True

        except Exception as e:
            print(f"[SYNC API] Failed to start server: {e}")
            return False

    def _server_loop(self):
        """Server loop that accepts connections"""
        while self.running:
            try:
                client_socket, addr = self.server_socket.accept()
                print(f"[SYNC API] External system connected: {addr}")
                self.client_socket = client_socket
                # Keep the connection open
                while self.running and self.client_socket:
                    try:
                        # Just keep the connection alive
                        time.sleep(0.1)
                    except Exception:
                        break
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    print(f"[SYNC API] Server error: {e}")
                break

    def send_sync(self, message, timeout_seconds=5.0):
        """Synchronous send to external system with automatic response handling"""
        print(f"[SYNC API] send_sync called, message: {message!r}")

        if not self.client_socket:
            print("[SYNC API] No external system connected")
            return False, None, "No external system connected"

        try:
            # Send the message using the socket directly
            print("[SYNC API] Writing to client...")
            self.client_socket.send(message.encode('utf-8'))
            print("[SYNC API] Write successful")

            # Read the response
            print("[SYNC API] Reading from client...")
            self.client_socket.settimeout(timeout_seconds)
            response = self.client_socket.recv(1024).decode('utf-8')
            print(f"[SYNC API] Read result: {response!r}")

            if response:
                print("[SYNC API] Returning success")
                return True, response, "Success"
            else:
                print("[SYNC API] Empty response")
                return False, None, "Empty response"

        except socket.timeout:
            print("[SYNC API] Read timeout")
            return False, None, "Read timeout"
        except Exception as e:
            print(f"[SYNC API] Exception: {e}")
            return False, None, f"Exception: {str(e)}"

    def close(self):
        """Close the TCP server"""
        self.running = False
        if self.client_socket:
            try:
                self.client_socket.close()
            except Exception:
                pass
            self.client_socket = None
        if self.server_socket:
            try:
                self.server_socket.close()
            except Exception:
                pass
            self.server_socket = None
        print("[SYNC API] Server closed")


# Global synchronous API manager instance
sync_api_manager = SynchronousAPIManager()


@registry.register(description="Setup synchronous API TCP server", category="sync_api")
def sync_api_setup_server(host, port):
    """Setup traditional TCP server for external system connections"""
    return sync_api_manager.setup_tcp_server(host, port)


@registry.register(description="Synchronous send to external system", category="sync_api")
def sync_api_send(message, timeout_seconds=5.0):
    """Send message to external system and wait for response"""
    return sync_api_manager.send_sync(message, timeout_seconds)


@registry.register(description="Close synchronous API server", category="sync_api")
def sync_api_close():
    """Close the synchronous API server"""
    sync_api_manager.close()


# --- Synchronous TCP Server Manager ---


class SyncTCPServerManager:
    def __init__(self):
        self.servers = {}  # server_id: socket
        self.clients = {}  # client_id: socket
        self.next_server_id = 10000
        self.next_client_id = 20000
        self.lock = threading.Lock()

    def create_server(self, host, port):
        with self.lock:
            server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_sock.bind((host, port))
            server_sock.listen(5)
            server_id = self.next_server_id
            self.next_server_id += 1
            self.servers[server_id] = server_sock
            return server_id

    def accept_client(self, server_id, timeout=10.0):
        server_sock = self.servers.get(server_id)
        if not server_sock:
            return False, None, "Server not found"
        server_sock.settimeout(timeout)
        try:
            client_sock, addr = server_sock.accept()
            client_id = self.next_client_id
            self.next_client_id += 1
            self.clients[client_id] = client_sock
            return True, client_id, f"Accepted from {addr}"
        except socket.timeout:
            return False, None, "Accept timeout"
        except Exception as e:
            return False, None, str(e)

    def close_server(self, server_id):
        server_sock = self.servers.pop(server_id, None)
        if server_sock:
            server_sock.close()
            return True
        return False

    def close_client(self, client_id):
        client_sock = self.clients.pop(client_id, None)
        if client_sock:
            client_sock.close()
            return True
        return False


# Global instance
sync_tcp_server_manager = SyncTCPServerManager()


@registry.register(description="Create synchronous TCP server", category="tcp_sync")
def tcp_server_create_sync(host, port):
    return sync_tcp_server_manager.create_server(host, port)


@registry.register(description="Accept client on synchronous TCP server", category="tcp_sync")
def tcp_server_accept_sync(server_id, timeout=10.0):
    server_sock = sync_tcp_server_manager.servers.get(server_id)
    if not server_sock:
        result = {"success": False, "client_id": None, "message": "Server not found"}
        if DEBUG_MODE:
            print(f"[PYDEBUG] tcp_server_accept_sync returning: {result}")
        return result
    server_sock.settimeout(timeout)
    try:
        client_sock, addr = server_sock.accept()
        client_id = sync_tcp_server_manager.next_client_id
        sync_tcp_server_manager.next_client_id += 1
        sync_tcp_server_manager.clients[client_id] = client_sock
        result = {"success": True, "client_id": int(client_id), "message": f"Accepted from {addr}"}
        if DEBUG_MODE:
            print(f"[PYDEBUG] tcp_server_accept_sync returning: {result}")
        return result
    except socket.timeout:
        result = {"success": False, "client_id": None, "message": "Accept timeout"}
        if DEBUG_MODE:
            print(f"[PYDEBUG] tcp_server_accept_sync returning: {result}")
        return result
    except Exception as e:
        result = {"success": False, "client_id": None, "message": str(e)}
        if DEBUG_MODE:
            print(f"[PYDEBUG] tcp_server_accept_sync returning: {result}")
        return result


@registry.register(description="Close synchronous TCP server", category="tcp_sync")
def tcp_server_close_sync(server_id):
    return sync_tcp_server_manager.close_server(server_id)


@registry.register(description="Connect to synchronous TCP server", category="tcp_sync")
def tcp_connect_to_sync_server(host, port):
    """Connect to a synchronous TCP server (not the async one)"""
    try:
        # Create a regular socket connection
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10.0)  # 10 second timeout
        sock.connect((host, port))

        # Generate a unique connection ID
        client_id = sync_tcp_server_manager.next_client_id
        sync_tcp_server_manager.next_client_id += 1

        # Store the socket in the sync manager for consistency
        sync_tcp_server_manager.clients[client_id] = sock
        result = {"success": True, "client_id": int(client_id), "message": "Connected to sync server"}
        if DEBUG_MODE:
            print(f"[PYDEBUG] tcp_connect_to_sync_server returning: {result}")
        return result
    except Exception as e:
        result = {"success": False, "client_id": None, "message": str(e)}
        if DEBUG_MODE:
            print(f"[PYDEBUG] tcp_connect_to_sync_server returning: {result}")
        return result


@registry.register(description="Write to synchronous TCP client", category="tcp_sync")
def tcp_write_sync_client(client_id, data):
    """Write data to a synchronous TCP client connection"""
    client_sock = sync_tcp_server_manager.clients.get(client_id)
    if not client_sock:
        result = {"success": False, "bytes_written": 0, "message": "Client not found"}
        if DEBUG_MODE:
            print(f"[PYDEBUG] tcp_write_sync_client returning: {result}")
        return result
    try:
        bytes_written = client_sock.send(data.encode('utf-8'))
        result = {"success": True, "bytes_written": bytes_written, "message": "Success"}
        if DEBUG_MODE:
            print(f"[PYDEBUG] tcp_write_sync_client returning: {result}")
        return result
    except Exception as e:
        result = {"success": False, "bytes_written": 0, "message": str(e)}
        if DEBUG_MODE:
            print(f"[PYDEBUG] tcp_write_sync_client returning: {result}")
        return result


@registry.register(description="Read from synchronous TCP client", category="tcp_sync")
def tcp_read_sync_client(client_id, max_bytes=1024):
    """Read data from a synchronous TCP client connection"""
    client_sock = sync_tcp_server_manager.clients.get(client_id)
    if not client_sock:
        result = {"success": False, "data": None, "message": "Client not found"}
        if DEBUG_MODE:
            print(f"[PYDEBUG] tcp_read_sync_client returning: {result}")
        return result
    try:
        data = client_sock.recv(max_bytes)
        if data:
            result = {"success": True, "data": data.decode('utf-8'), "message": "Success"}
            if DEBUG_MODE:
                print(f"[PYDEBUG] tcp_read_sync_client returning: {result}")
            return result
        else:
            result = {"success": False, "data": None, "message": "Connection closed"}
            if DEBUG_MODE:
                print(f"[PYDEBUG] tcp_read_sync_client returning: {result}")
            return result
    except Exception as e:
        result = {"success": False, "data": None, "message": str(e)}
        if DEBUG_MODE:
            print(f"[PYDEBUG] tcp_read_sync_client returning: {result}")
        return result


@registry.register(description="Close synchronous TCP client", category="tcp_sync")
def tcp_close_sync_client(client_id):
    """Close a synchronous TCP client connection"""
    return sync_tcp_server_manager.close_client(client_id)


# --- Synchronous functions for async server connections ---
@registry.register(description="Synchronous write to async server client", category="tcp_server")
def tcp_server_write_sync(client_id, data):
    """Synchronous write to a client connected to an async TCP server"""
    try:
        # Get the client connection from the network manager
        reader, writer = network_manager.tcp_connections.get(client_id, (None, None))
        if not writer:
            return False, f"Client {client_id} not found"

        if isinstance(data, str):
            data_bytes = data.encode("utf-8")
        else:
            data_bytes = bytes(data)

        # Use asyncio to write synchronously
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            writer.write(data_bytes)
            loop.run_until_complete(writer.drain())
            return True, f"Sent {len(data_bytes)} bytes to client {client_id}"
        finally:
            loop.close()

    except Exception as e:
        return False, f"Write error: {str(e)}"


@registry.register(description="Synchronous read from async server client", category="tcp_server")
def tcp_server_read_sync(client_id, max_bytes=1024):
    """Synchronous read from a client connected to an async TCP server"""
    try:
        # Get the client connection from the network manager
        reader, writer = network_manager.tcp_connections.get(client_id, (None, None))
        if not reader:
            return False, None, f"Client {client_id} not found"

        # Use asyncio to read synchronously
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            data = loop.run_until_complete(reader.read(max_bytes))
            if data:
                data_str = data.decode("utf-8", errors="ignore")
                return True, data_str, f"Received {len(data)} bytes from client {client_id}"
            else:
                # Connection closed
                network_manager.tcp_connections.pop(client_id, None)
                return False, None, f"Client {client_id} disconnected"
        finally:
            loop.close()

    except Exception as e:
        return False, None, f"Read error: {str(e)}"
