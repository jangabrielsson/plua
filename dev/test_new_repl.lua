-- Test the new asyncio REPL functionality
-- This script tests the start_repl, stop_repl, and get_repl_status functions

print("Testing new asyncio REPL functions...")

-- Test getting status when REPL is not running
local status = _PY.get_repl_status()
print("Initial REPL status:", status)

-- Test starting the REPL
print("Starting REPL...")
local start_result = _PY.start_repl()
print("Start result:", start_result)

-- Test getting status when REPL is running
local status_running = _PY.get_repl_status()
print("REPL status after start:", status_running)

-- Test stopping the REPL
print("Stopping REPL...")
local stop_result = _PY.stop_repl()
print("Stop result:", stop_result)

-- Test getting status after stopping
local status_stopped = _PY.get_repl_status()
print("REPL status after stop:", status_stopped)

-- Test clientPrint with clientId=0 (should go to stdout)
print("Testing clientPrint with clientId=0:")
_PY.clientPrint(0, "This message should appear on stdout via clientPrint")

print("REPL function tests completed!")

-- Keep the script running for a moment
_PY.setTimeout(function()
    print("Test script finishing...")
end, 1000)
