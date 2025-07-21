
-- Fibaro system is loaded with --fibaro flag
--%%offline:true

print("Hello")

local devs = api.hc3.get("/devices")
print("Devices:", #devs)

local devs2 = api.get("/devices/1")
print("Device 1:", devs2.name, "Type:", devs2.type)