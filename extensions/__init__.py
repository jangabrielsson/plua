"""
Extensions package for PLua
Contains all extension modules and the registry system
"""

from .registry import LuaExtensionRegistry, registry, get_lua_extensions
import extensions.html_extensions  # noqa: F401

__all__ = ['LuaExtensionRegistry', 'registry', 'get_lua_extensions']
