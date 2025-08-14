-- Simple test to verify _PY.http_server_respond exists

print("Testing _PY.http_server_respond function:")
print("Function exists:", _PY.http_server_respond and "YES" or "NO")

if _PY.http_server_respond then
  print("Calling with test args...")
  local result = _PY.http_server_respond("test_id", "test_data", 200, "text/plain", {["test"] = "value"})
  print("Result:", result)
else
  print("Function not found!")
end
