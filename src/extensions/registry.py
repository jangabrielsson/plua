"""
Lua Extension Registry
Provides the decorator system for automatically registering Python functions to the Lua environment.
"""

from typing import Dict, Any, Callable, Optional
from functools import wraps


class LuaExtensionRegistry:
    """Registry for Lua extensions that will be automatically added to the Lua environment"""

    def __init__(self):
        self._extensions: Dict[str, Callable] = {}
        self._extension_metadata: Dict[str, Dict[str, Any]] = {}

    def register(self, name: Optional[str] = None, description: str = "", category: str = "general", inject_runtime: bool = False):
        """
        Decorator to register a Python function for automatic addition to the Lua environment.

        Args:
            name: Optional custom name for the function in Lua (defaults to function name)
            description: Description of what the function does
            category: Category for grouping functions (e.g., 'timers', 'io', 'math')
            inject_runtime: If True, the Lua runtime will be passed as the first argument
        """
        def decorator(func: Callable) -> Callable:
            func_name = name or func.__name__

            # Store the function and metadata
            self._extensions[func_name] = (func, inject_runtime)
            self._extension_metadata[func_name] = {
                'description': description,
                'category': category,
                'original_func': func,
                'inject_runtime': inject_runtime
            }

            # Add metadata to the function for introspection
            func.lua_metadata = {
                'name': func_name,
                'description': description,
                'category': category,
                'inject_runtime': inject_runtime
            }

            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            # Copy metadata to wrapper
            wrapper.lua_metadata = func.lua_metadata

            return wrapper
        return decorator

    def get_extensions(self) -> Dict[str, Callable]:
        """Get all registered extensions"""
        return self._extensions.copy()

    def get_extension_metadata(self) -> Dict[str, Dict[str, Any]]:
        """Get metadata for all extensions"""
        return self._extension_metadata.copy()

    def get_extensions_by_category(self, category: str) -> Dict[str, Callable]:
        """Get extensions filtered by category"""
        return {
            name: func for name, func in self._extensions.items()
            if self._extension_metadata[name]['category'] == category
        }

    def list_extensions(self) -> None:
        """Print a formatted list of all available extensions"""
        print("Available Lua Extensions:")
        print("=" * 50)

        categories = {}
        for name, metadata in self._extension_metadata.items():
            category = metadata['category']
            if category not in categories:
                categories[category] = []
            categories[category].append((name, metadata['description']))

        for category in sorted(categories.keys()):
            print(f"\n{category.upper()}:")
            for name, description in sorted(categories[category]):
                print(f"  {name}: {description}")


# Global registry instance
registry = LuaExtensionRegistry()


# Helper function to get all extensions for Lua environment
def get_lua_extensions(lua_runtime=None):
    """Get all registered extensions for the Lua environment, organized in a _PY table"""
    exts = registry.get_extensions()

    # Create the _PY table structure as a proper Lua table
    if lua_runtime is not None:
        py_table = lua_runtime.table()

        for name, (func, inject_runtime) in exts.items():
            if inject_runtime:
                # Bind the runtime as the first argument
                def make_bound(f):
                    return lambda *args, **kwargs: f(lua_runtime, *args, **kwargs)
                py_table[name] = make_bound(func)
            else:
                py_table[name] = func

        return py_table
    else:
        # Fallback for when no runtime is provided
        py_table = {}
        for name, (func, inject_runtime) in exts.items():
            py_table[name] = func
        return py_table
