-- network_utils.lua - Network utility functions
local utils = require("utils")

local network_utils = {}

-- Function to test a TCP connection with formatted output
function network_utils.test_tcp_connection(host, port, callback)
  local formatted_host = utils.format_with_prefix("Testing", host .. ":" .. port)
  print(formatted_host)
  
  tcp_connect(host, port, function(success, conn_id, message)
  local result = utils.format_with_prefix("Result", success and "SUCCESS" or "FAILED")
  print(result, message)
  
  if success then
  tcp_close(conn_id, function(close_success, close_message)
  print(utils.format_with_prefix("Close", close_success and "SUCCESS" or "FAILED"))
  if callback then
  callback(success, conn_id, message)
  end
  end)
  else
  if callback then
  callback(success, conn_id, message)
  end
  end
  end)
end

-- Function to get network info with formatted output
function network_utils.get_network_info()
  local info = utils.create_table(
  "hostname", _PY.get_hostname(),
  "local_ip", get_local_ip(),
  "port_80_available", is_port_available(80),
  "port_8080_available", is_port_available(8080)
  )
  
  print(utils.format_with_prefix("Network Info", "Retrieved"))
  for key, value in pairs(info) do
  print("  " .. utils.capitalize(key) .. ":", value)
  end
  
  return info
end

-- Function to perform a simple network test
function network_utils.quick_test()
  print(utils.format_with_prefix("Network Test", "Starting"))
  
  -- Test local network info
  network_utils.get_network_info()
  
  -- Test a simple connection
  network_utils.test_tcp_connection("google.com", 80, function(success, conn_id, message)
  print(utils.format_with_prefix("Quick Test", success and "COMPLETED" or "FAILED"))
  end)
end

-- Return the module
return network_utils 