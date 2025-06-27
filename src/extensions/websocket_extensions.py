"""
WebSocket Extensions for PLua
Provides WebSocket client functionality compatible with Fibaro HC3 API
"""

import threading
import sys
from .registry import registry
from extensions.core import timer_gate
from extensions.network_extensions import loop_manager
import websockets


class WebSocketManager:
    """Manages WebSocket connections with event-driven callbacks"""

    def __init__(self):
        self.connections = {}  # conn_id: WebSocketConnection
        self.next_id = 1
        self.lock = threading.Lock()
        self.active_operations = 0
        self.active_callbacks = 0

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

    def _increment_callbacks(self):
        with self.lock:
            self.active_callbacks += 1

    def _decrement_callbacks(self):
        with self.lock:
            self.active_callbacks -= 1

    def has_active_operations(self):
        """Check if there are any active WebSocket operations"""
        with self.lock:
            return (
                self.active_operations > 0
                or len(self.connections) > 0
                or self.active_callbacks > 0
            )

    def force_cleanup(self):
        """Force cleanup of all WebSocket connections"""
        with self.lock:
            for conn_id in list(self.connections.keys()):
                try:
                    connection = self.connections[conn_id]
                    if connection:
                        connection.close()
                except Exception:
                    pass
            self.connections.clear()
            self.active_operations = 0
            self.active_callbacks = 0


class WebSocketConnection:
    """Represents a single WebSocket connection"""

    def __init__(self, conn_id, manager, use_tls=False):
        self.conn_id = conn_id
        self.manager = manager
        self.use_tls = use_tls
        self.ws = None
        self.connected = False
        self.event_listeners = {
            'connected': [],
            'disconnected': [],
            'error': [],
            'dataReceived': []
        }
        self.thread = None
        self.should_stop = False

    def add_event_listener(self, event_name, callback):
        """Add an event listener"""
        if event_name in self.event_listeners:
            self.event_listeners[event_name].append(callback)

    def _emit_event(self, event_name, *args):
        """Emit an event to all registered listeners"""
        if event_name in self.event_listeners:
            for callback in self.event_listeners[event_name]:
                try:
                    # Use timer gate to control callback execution
                    def run_callback():
                        try:
                            callback(*args)
                        except Exception as e:
                            print(f"Error in WebSocket {event_name} callback: {e}", file=sys.stderr)
                        finally:
                            self.manager._decrement_callbacks()

                    self.manager._increment_callbacks()
                    timer_gate.run_or_queue(run_callback)
                except Exception as e:
                    print(f"Error scheduling WebSocket {event_name} callback: {e}", file=sys.stderr)

    def connect(self, url, headers=None):
        """Connect to WebSocket server"""
        self.manager._increment_operations()

        def connect_thread():
            try:
                import websocket

                # Ensure proper URL scheme
                if not url.startswith(('ws://', 'wss://')):
                    raise ValueError(f"Invalid WebSocket URL scheme: {url}")

                # Convert Lua table headers to Python list format if provided
                python_headers = None
                if headers:
                    try:
                        # Convert Lua table to Python list of strings in "Key: Value" format
                        python_headers = []
                        for key, value in headers.items():
                            python_headers.append(f"{key}: {value}")
                    except Exception as e:
                        print(f"Error converting headers: {e}", file=sys.stderr)
                        python_headers = None

                # Create WebSocket connection with optional headers
                self.ws = websocket.WebSocketApp(
                    url,
                    header=python_headers,  # Pass headers as list of strings
                    on_open=self._on_open,
                    on_message=self._on_message,
                    on_error=self._on_error,
                    on_close=self._on_close
                )

                # Run the WebSocket in a separate thread
                self.ws.run_forever()

            except Exception as e:
                self._emit_event('error', str(e))
            finally:
                self.manager._decrement_operations()

        self.thread = threading.Thread(target=connect_thread, daemon=True)
        self.thread.start()

    def _on_open(self, ws):
        """Called when WebSocket connection is opened"""
        self.connected = True
        self._emit_event('connected')

    def _on_message(self, ws, message):
        """Called when a message is received"""
        self._emit_event('dataReceived', message)

    def _on_error(self, ws, error):
        """Called when an error occurs"""
        self._emit_event('error', str(error))

    def _on_close(self, ws, close_status_code, close_msg):
        """Called when WebSocket connection is closed"""
        self.connected = False
        self._emit_event('disconnected')

    def send(self, data):
        """Send data through the WebSocket"""
        if self.ws and self.connected:
            try:
                self.ws.send(data)
                return True
            except Exception as e:
                self._emit_event('error', f"Send error: {str(e)}")
                return False
        else:
            self._emit_event('error', "WebSocket not connected")
            return False

    def is_open(self):
        """Check if the WebSocket connection is open"""
        return self.connected and self.ws is not None

    def close(self):
        """Close the WebSocket connection"""
        self.should_stop = True
        if self.ws:
            try:
                self.ws.close()
            except Exception:
                pass
        self.connected = False
        # Remove from manager
        self.manager.connections.pop(self.conn_id, None)


# Global WebSocket manager instance
websocket_manager = WebSocketManager()


# WebSocket Extension Functions
@registry.register(description="Create WebSocket client", category="websocket")
def websocket_client_create(use_tls=False):
    """Create a new WebSocket client connection"""
    conn_id = websocket_manager._next_conn_id()
    connection = WebSocketConnection(conn_id, websocket_manager, use_tls)
    websocket_manager.connections[conn_id] = connection
    return conn_id


@registry.register(description="Add event listener to WebSocket", category="websocket")
def websocket_add_event_listener(conn_id, event_name, callback):
    """Add an event listener to a WebSocket connection"""
    connection = websocket_manager.connections.get(conn_id)
    if connection:
        connection.add_event_listener(event_name, callback)
        return True
    return False


@registry.register(description="Connect WebSocket to URL", category="websocket")
def websocket_connect(conn_id, url, headers=None):
    """Connect WebSocket to the specified URL with optional headers"""
    connection = websocket_manager.connections.get(conn_id)
    if connection:
        connection.connect(url, headers)
        return True
    return False


@registry.register(description="Send data through WebSocket", category="websocket")
def websocket_send(conn_id, data):
    """Send data through the WebSocket connection"""
    connection = websocket_manager.connections.get(conn_id)
    if connection:
        return connection.send(data)
    return False


@registry.register(description="Check if WebSocket is open", category="websocket")
def websocket_is_open(conn_id):
    """Check if the WebSocket connection is open"""
    connection = websocket_manager.connections.get(conn_id)
    if connection:
        return connection.is_open()
    return False


@registry.register(description="Close WebSocket connection", category="websocket")
def websocket_close(conn_id):
    """Close the WebSocket connection"""
    connection = websocket_manager.connections.get(conn_id)
    if connection:
        connection.close()
        return True
    return False


@registry.register(description="Check if there are active WebSocket operations", category="websocket")
def has_active_websocket_operations():
    """Check if there are any active WebSocket operations"""
    return websocket_manager.has_active_operations()


class WebSocketServerManager:
    def __init__(self):
        self.servers = {}  # server_id: WebSocketServer
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


class WebSocketServer:
    def __init__(self, server_id, manager):
        self.server_id = server_id
        self.manager = manager
        self.server = None
        self.clients = set()
        self.event_listeners = {
            'client_connected': [],
            'client_disconnected': [],
            'message': [],
            'error': []
        }
        self.loop = None
        self.running = False

    def add_event_listener(self, event_name, callback):
        if event_name in self.event_listeners:
            self.event_listeners[event_name].append(callback)

    def _emit_event(self, event_name, *args):
        if event_name in self.event_listeners:
            for callback in self.event_listeners[event_name]:
                try:
                    def run_callback():
                        try:
                            callback(*args)
                        except Exception as e:
                            print(f"Error in WebSocketServer {event_name} callback: {e}", file=sys.stderr)
                        finally:
                            self.manager._decrement_callbacks()
                    self.manager._increment_callbacks()
                    timer_gate.run_or_queue(run_callback)
                except Exception as e:
                    print(f"Error scheduling WebSocketServer {event_name} callback: {e}", file=sys.stderr)

    async def _handler(self, websocket, path):
        self.clients.add(websocket)
        self._emit_event('client_connected', websocket)
        try:
            async for message in websocket:
                self._emit_event('message', websocket, message)
        except Exception as e:
            self._emit_event('error', str(e))
        finally:
            self.clients.discard(websocket)
            self._emit_event('client_disconnected', websocket)

    def start(self, host, port):
        self.manager._increment_operations()

        async def start_server():
            try:
                async def handler(websocket, path=None):
                    await self._handler(websocket, path)
                self.server = await websockets.serve(handler, host, port)
                self.running = True
            except Exception as e:
                self._emit_event('error', str(e))
            finally:
                self.manager._decrement_operations()
        loop_manager.create_task(start_server())

    def send(self, websocket, data):
        async def send_msg():
            try:
                await websocket.send(data)
            except Exception as e:
                self._emit_event('error', f"Send error: {str(e)}")
        loop_manager.create_task(send_msg())

    def close(self):
        if self.server:
            self.server.close()
            self.running = False
        self.manager.servers.pop(self.server_id, None)


# Global WebSocket server manager instance
websocket_server_manager = WebSocketServerManager()


@registry.register(description="Create WebSocket server", category="websocket_server")
def websocket_server_create():
    server_id = websocket_server_manager._next_server_id()
    server = WebSocketServer(server_id, websocket_server_manager)
    websocket_server_manager.servers[server_id] = server
    return server_id


@registry.register(description="Add event listener to WebSocket server", category="websocket_server")
def websocket_server_add_event_listener(server_id, event_name, callback):
    server = websocket_server_manager.servers.get(server_id)
    if server:
        server.add_event_listener(event_name, callback)


@registry.register(description="Start WebSocket server", category="websocket_server")
def websocket_server_start(server_id, host, port):
    server = websocket_server_manager.servers.get(server_id)
    if server:
        server.start(host, port)


@registry.register(description="Send data to WebSocket client", category="websocket_server")
def websocket_server_send(server_id, websocket, data):
    server = websocket_server_manager.servers.get(server_id)
    if server:
        server.send(websocket, data)


@registry.register(description="Close WebSocket server", category="websocket_server")
def websocket_server_close(server_id):
    server = websocket_server_manager.servers.get(server_id)
    if server:
        server.close()


@registry.register(description="Check if there are active WebSocket server operations", category="websocket_server")
def has_active_websocket_server_operations():
    return websocket_server_manager.has_active_operations()
