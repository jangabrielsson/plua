#!/usr/bin/env python3

import asyncio
from src.plua.runtime import LuaAsyncRuntime

async def test_timer_debug():
    runtime = LuaAsyncRuntime()
    runtime.initialize_lua()
    
    print("Creating timer...")
    
    script = """
    test_executed = false  -- Global variable
    print("About to create timer")
    setTimeout(function()
        print("Timer callback is executing!")
        test_executed = true
        print("Timer callback finished, test_executed should be true")
    end, 100)  -- 100ms delay
    print("Timer created")
    """
    
    runtime.interpreter.lua.execute(script)
    print("Script executed, waiting for timer...")
    
    # Wait for timer to execute
    await asyncio.sleep(0.2)
    
    # Check result
    result = runtime.interpreter.lua.eval("test_executed")
    print(f"Timer executed: {result}")
    
    # Wait a bit longer to see if there are any delayed effects
    await asyncio.sleep(0.5)
    result = runtime.interpreter.lua.eval("test_executed")
    print(f"Timer executed (after extra wait): {result}")

if __name__ == "__main__":
    asyncio.run(test_timer_debug())
