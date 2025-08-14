# PyLib - PLua FFI Libraries Package
"""
This package contains Python libraries that can be dynamically loaded from Lua 
using the FFI-like interface provided by PLua.

Each module in this package should use @export_to_lua() decorators to expose
functions that can be called from Lua scripts.
"""

# Import all bundled libraries to ensure they're available for dynamic loading
# This registers their @export_to_lua decorated functions

try:
    from . import filesystem
except ImportError:
    pass

try:
    from . import http_client
except ImportError:
    pass

try:
    from . import tcp_client
except ImportError:
    pass

try:
    from . import udp_client
except ImportError:
    pass

try:
    from . import websocket_client
except ImportError:
    pass

try:
    from . import mqtt_client
except ImportError:
    pass
