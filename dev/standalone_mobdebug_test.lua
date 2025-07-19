-- Standalone Lua script with MobDebug for testing VS Code extension
-- This uses the system's MobDebug, not our custom version
local mobdebug = require("mobdebug")
mobdebug.start()

print("Starting standalone test...")
local x = 1
print("x =", x)
x = x + 1
print("x =", x)
print("Test complete")
