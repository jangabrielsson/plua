print("=== MINIMAL TIMER TEST ===")
print("Setting up timer...")

setTimeout(function()
    print("TIMER CALLBACK FIRED!")
end, 100)

print("Timer set up, waiting...")

-- Keep the coroutine alive
while true do
    _PY.sleep(1)
end 