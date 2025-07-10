"""
Extensions package for PLua
Contains all extension modules and the registry system
"""

from .registry import LuaExtensionRegistry, registry, get_lua_extensions

# Import all extensions at startup to register their functions
import extensions.core  # noqa: F401
import extensions.html_extensions  # noqa: F401
import extensions.websocket_extensions  # noqa: F401
import extensions.network_extensions  # noqa: F401
import extensions.web_server  # noqa: F401

__all__ = ['LuaExtensionRegistry', 'registry', 'get_lua_extensions']

# Lazy loading registry
_loaded_extensions = set()


def _load_extension_if_needed(extension_name):
    """Load an extension module only when it's first used"""
    if extension_name not in _loaded_extensions:
        if extension_name == 'html_extensions':
            import extensions.html_extensions  # noqa: F401
        elif extension_name == 'websocket_extensions':
            import extensions.websocket_extensions  # noqa: F401
        elif extension_name == 'network_extensions':
            import extensions.network_extensions  # noqa: F401
        elif extension_name == 'web_server':
            import extensions.web_server  # noqa: F401
        _loaded_extensions.add(extension_name)


def get_extension_function(func_name):
    """Get an extension function, loading the module if needed"""
    # Check which extension contains this function
    if func_name.startswith('html_') or func_name in ['render_html', 'html_to_console']:
        _load_extension_if_needed('html_extensions')
    elif func_name.startswith('websocket_') or func_name in ['websocket_connect', 'websocket_send']:
        _load_extension_if_needed('websocket_extensions')
    elif func_name.startswith('tcp_') or func_name.startswith('http_') or func_name.startswith('udp_'):
        _load_extension_if_needed('network_extensions')
    elif func_name.startswith('web_server_'):
        _load_extension_if_needed('web_server')
    
    # Return the function from the registry
    return registry.get_function(func_name)
