#!/usr/bin/env python3
"""
Simple test to verify lupa import works
"""

try:
    from lupa import LuaRuntime
    print("✅ lupa import successful")
    
    # Test basic functionality
    lua = LuaRuntime()
    result = lua.execute("return 2 + 2")
    print(f"✅ Lua execution successful: 2 + 2 = {result}")
    
except ImportError as e:
    print(f"❌ lupa import failed: {e}")
except Exception as e:
    print(f"❌ lupa test failed: {e}") 