-- Test callback system with parameters

print("Testing callback system...")

-- Test timer callback (should work)
setTimeout(function()
  print("Timer callback executed!")
end, 1000)

-- Test network callback (should work with new system)
_PY.tcp_connect("tcpbin.com", 4242, function(success, conn_id, message)
  print("Network callback executed!")
  print("Success:", success)
  print("Conn ID:", conn_id)
  print("Message:", message)
end)

print("Callbacks registered, waiting...") 