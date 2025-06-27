"""
Web Server Extension for PLua
Provides a web server that runs in a separate process and communicates via message queue
"""

import json
import threading
import multiprocessing
import queue
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from .registry import registry

# Global web server instance for tracking
_web_server_instance = None
_execution_tracker = None


def set_execution_tracker(tracker):
    """Set the execution tracker for web server state tracking"""
    global _execution_tracker
    _execution_tracker = tracker


def notify_web_server_state(running):
    """Notify execution tracker of web server state change"""
    global _execution_tracker
    if _execution_tracker:
        _execution_tracker.set_web_server_running(running)


class WebServerRequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the web server"""

    def __init__(self, *args, message_queue=None, **kwargs):
        self.message_queue = message_queue
        super().__init__(*args, **kwargs)

    def do_GET(self):
        """Handle GET requests"""
        try:
            parsed_url = urlparse(self.path)
            path = parsed_url.path
            query_params = parse_qs(parsed_url.query)

            # Send message to Lua process
            message = {
                "type": "http_request",
                "method": "GET",
                "path": path,
                "query": query_params,
                "headers": dict(self.headers),
                "body": None
            }

            if self.message_queue:
                self.message_queue.put(message)

            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            response = {
                "status": "received",
                "path": path,
                "method": "GET"
            }
            self.wfile.write(json.dumps(response).encode())

        except Exception as e:
            self.send_error(500, str(e))

    def do_POST(self):
        """Handle POST requests"""
        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else ""

            parsed_url = urlparse(self.path)
            path = parsed_url.path
            query_params = parse_qs(parsed_url.query)

            # Try to parse JSON body
            try:
                json_body = json.loads(body) if body else None
            except json.JSONDecodeError:
                json_body = None

            # Send message to Lua process
            message = {
                "type": "http_request",
                "method": "POST",
                "path": path,
                "query": query_params,
                "headers": dict(self.headers),
                "body": json_body if json_body else body
            }

            if self.message_queue:
                self.message_queue.put(message)

            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            response = {
                "status": "received",
                "path": path,
                "method": "POST",
                "body_length": len(body)
            }
            self.wfile.write(json.dumps(response).encode())

        except Exception as e:
            self.send_error(500, str(e))

    def do_PUT(self):
        """Handle PUT requests"""
        self.do_POST()  # Same handling as POST

    def do_DELETE(self):
        """Handle DELETE requests"""
        try:
            parsed_url = urlparse(self.path)
            path = parsed_url.path
            query_params = parse_qs(parsed_url.query)

            # Send message to Lua process
            message = {
                "type": "http_request",
                "method": "DELETE",
                "path": path,
                "query": query_params,
                "headers": dict(self.headers),
                "body": None
            }

            if self.message_queue:
                self.message_queue.put(message)

            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            response = {
                "status": "received",
                "path": path,
                "method": "DELETE"
            }
            self.wfile.write(json.dumps(response).encode())

        except Exception as e:
            self.send_error(500, str(e))

    def log_message(self, format, *args):
        """Override to reduce logging noise"""
        pass


class WebServerProcess:
    """Web server that runs in a separate process"""

    def __init__(self, port=8080, host="0.0.0.0"):
        self.port = port
        self.host = host
        self.process = None
        self.message_queue = None
        self.server = None
        self.running = False

    def start(self):
        """Start the web server in a separate process"""
        if self.process and self.process.is_alive():
            return False, "Server already running"

        # Create message queue for inter-process communication
        self.message_queue = multiprocessing.Queue()

        # Start server process
        self.process = multiprocessing.Process(
            target=self._run_server,
            args=(self.host, self.port, self.message_queue)
        )
        self.process.daemon = True
        self.process.start()

        # Wait a moment for server to start
        time.sleep(0.5)

        if self.process.is_alive():
            self.running = True
            notify_web_server_state(True)
            return True, f"Web server started on {self.host}:{self.port}"
        else:
            return False, "Failed to start web server"

    def stop(self):
        """Stop the web server"""
        if self.process and self.process.is_alive():
            self.process.terminate()
            self.process.join(timeout=2)
            if self.process.is_alive():
                self.process.kill()
            self.running = False
            notify_web_server_state(False)
            return True, "Web server stopped"
        return False, "Server not running"

    def is_running(self):
        """Check if server is running"""
        return self.process and self.process.is_alive()

    def get_message(self, timeout=0.1):
        """Get a message from the server (non-blocking)"""
        if not self.message_queue:
            return None

        try:
            return self.message_queue.get_nowait()
        except queue.Empty:
            return None

    def _run_server(self, host, port, message_queue):
        """Run the HTTP server"""
        try:
            # Create custom request handler with message queue
            def handler(*args, **kwargs):
                return WebServerRequestHandler(*args, message_queue=message_queue, **kwargs)

            # Create and start server
            self.server = HTTPServer((host, port), handler)
            print(f"Web server started on {host}:{port}")
            self.server.serve_forever()

        except Exception as e:
            print(f"Web server error: {e}")
        finally:
            if self.server:
                self.server.shutdown()


# Global web server instance
web_server = None


@registry.register(description="Start web server for receiving HTTP callbacks", category="web_server")
def start_web_server(port=8080, host="0.0.0.0"):
    """Start web server in separate process"""
    global web_server, _web_server_instance

    if web_server and web_server.is_running():
        return False, "Web server already running"

    web_server = WebServerProcess(port, host)
    _web_server_instance = web_server
    success, message = web_server.start()

    return success, message


@registry.register(description="Stop web server", category="web_server")
def stop_web_server():
    """Stop web server"""
    global web_server, _web_server_instance

    if not web_server:
        return False, "No web server running"

    success, message = web_server.stop()
    if success:
        _web_server_instance = None
    return success, message


@registry.register(description="Check if web server is running", category="web_server")
def is_web_server_running():
    """Check if web server is running"""
    global web_server

    if not web_server:
        return False

    return web_server.is_running()


@registry.register(description="Get next HTTP request from web server", category="web_server")
def get_web_server_message():
    """Get next message from web server (non-blocking)"""
    global web_server

    if not web_server:
        return None

    return web_server.get_message()


@registry.register(description="Get web server status", category="web_server")
def get_web_server_status():
    """Get web server status information"""
    global web_server

    if not web_server:
        return {
            "running": False,
            "port": None,
            "host": None,
            "process_id": None
        }

    return {
        "running": web_server.is_running(),
        "port": web_server.port,
        "host": web_server.host,
        "process_id": web_server.process.pid if web_server.process else None
    }


# Lua callback registration system
lua_callbacks = {}


@registry.register(description="Register callback for web server events", category="web_server", inject_runtime=True)
def register_web_callback(lua_runtime, event_type, callback):
    """Register a Lua callback for web server events"""
    global lua_callbacks

    if event_type not in lua_callbacks:
        lua_callbacks[event_type] = []

    lua_callbacks[event_type].append(callback)
    return True, f"Callback registered for {event_type}"


@registry.register(description="Unregister callback for web server events", category="web_server")
def unregister_web_callback(event_type, callback):
    """Unregister a Lua callback for web server events"""
    global lua_callbacks

    if event_type in lua_callbacks and callback in lua_callbacks[event_type]:
        lua_callbacks[event_type].remove(callback)
        return True, f"Callback unregistered for {event_type}"

    return False, f"No callback found for {event_type}"


def trigger_lua_callbacks(event_type, data):
    """Trigger Lua callbacks for a specific event type"""
    global lua_callbacks

    if event_type not in lua_callbacks:
        return

    for callback in lua_callbacks[event_type]:
        try:
            # Execute callback in Lua
            callback(data)
        except Exception as e:
            print(f"Error in web server callback: {e}")


# Message processing thread
message_processor = None
message_processor_running = False


def start_message_processor(lua_runtime):
    """Start message processing thread"""
    global message_processor, message_processor_running

    if message_processor_running:
        return

    def process_messages():
        global message_processor_running
        message_processor_running = True

        while message_processor_running:
            try:
                if web_server:
                    message = web_server.get_message()
                    if message:
                        # Trigger Lua callbacks
                        trigger_lua_callbacks("http_request", message)

                time.sleep(0.1)  # Small delay to prevent busy waiting

            except Exception as e:
                print(f"Error in message processor: {e}")
                time.sleep(1)  # Longer delay on error

    message_processor = threading.Thread(target=process_messages, daemon=True)
    message_processor.start()


@registry.register(description="Start message processing for web server", category="web_server", inject_runtime=True)
def start_web_message_processing(lua_runtime):
    """Start processing web server messages and trigger Lua callbacks"""
    start_message_processor(lua_runtime)
    return True, "Message processing started"


@registry.register(description="Stop message processing for web server", category="web_server")
def stop_web_message_processing():
    """Stop processing web server messages"""
    global message_processor_running

    message_processor_running = False
    return True, "Message processing stopped"
