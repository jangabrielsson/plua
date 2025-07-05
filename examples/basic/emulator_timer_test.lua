-- Test emulator timer functionality
print("Loading emulator...")
local emulator = require("plua.emulator")

print("Creating emulator instance...")
local emu = emulator.Emulator(plua)

print("Loading QuickApp file...")
emu:loadMainFile("examples/fibaro/QA_basic.lua")

print("Test completed - emulator should have started the QuickApp with timer") 