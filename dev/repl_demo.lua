-- Simple REPL demo
-- This script starts the REPL and lets you interact with it

print("🚀 Starting PLua REPL Demo")
print("The asyncio REPL will start shortly...")
print("Once it starts, you can type Lua commands and see the results.")
print("Type 'exit' or 'quit' to stop the REPL.")
print("")

-- Start the REPL
local result = _PY.start_repl()
print("REPL start result:", result)
print("REPL status:", _PY.get_repl_status())
print("")

-- Keep the main script running indefinitely so the REPL can work
-- The REPL will handle input/output on its own
print("PLua script will now wait for REPL interaction...")
print("Press Ctrl+C to exit entirely.")

-- Set up a background timer to keep the script alive
local function keepAlive()
    _PY.setTimeout(keepAlive, 10000) -- Keep alive every 10 seconds
end
keepAlive()
