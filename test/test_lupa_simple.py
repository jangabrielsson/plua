#!/usr/bin/env python3
"""
Simple test to verify lupa import works
"""

try:
    from lupa import LuaRuntime
    print("SUCCESS: lupa import successful")
    
    # Test basic functionality
    lua = LuaRuntime()
    result = lua.execute("return 2 + 2")
    print(f"SUCCESS: Lua execution successful: 2 + 2 = {result}")
    
except ImportError as e:
    print(f"ERROR: lupa import failed: {e}")
except Exception as e:
    print(f"ERROR: lupa test failed: {e}") 