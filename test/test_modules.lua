-- Test script to demonstrate Lua modules
print("=== Lua Module Test ===")

-- Note: utils and network_utils modules have been removed
-- This test now demonstrates direct use of _PY functions

print("\n--- Testing _PY functions directly ---")

-- Test network utility functions
print("\n--- Testing network utilities ---")
local hostname = _PY.get_hostname()
local local_ip = _PY.get_local_ip()
local port_80_available = _PY.is_port_available(80)
local port_8080_available = _PY.is_port_available(8080)

print("Network Info:")
print("  Hostname:", hostname)
print("  Local IP:", local_ip)
print("  Port 80 available:", port_80_available)
print("  Port 8080 available:", port_8080_available)

-- Test a simple network connection using _PY functions directly
print("\n--- Testing network connection ---")
local success, conn_id, message = _PY.tcp_connect_sync("google.com", 80)
if success then
  print("Connection test: SUCCESS -", message)
  _PY.tcp_close_sync(conn_id)
  print("Connection closed")
else
  print("Connection test: FAILED -", message)
end

print("\n=== Module test completed ===") 