-- Very simple test for MobDebug
print("Starting simple test...")
local x = 1
print("x =", x)
x = x + 1
print("x =", x)
print("Test complete")

print(_PY.json_encode({"a", "b", "c"}))
