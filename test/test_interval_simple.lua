-- Simple interval test
print("Creating interval...")
local id = _PY.setInterval(function()
    print("✓ Interval fired!")
end, 1000)

print("Interval ID:", id)
print("ID type:", type(id))

-- Wait a bit
for i = 1, 50 do
    _PY.yield_to_loop()
end

print("Done!") 