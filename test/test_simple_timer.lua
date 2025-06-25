-- Very simple timer test
print("Creating timer...")

_PY.setTimeout(function()
    print("✓ Timer executed!")
end, 1000)

print("Timer created. Waiting...")

-- Just wait without any complex logic
for i = 1, 200 do  -- Wait for 2 seconds
    _PY.yield_to_loop()
end

print("Done!") 