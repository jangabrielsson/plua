-- Test script that starts telnet server
print("🚀 Testing PLua telnet server mode")

-- The telnet server will start automatically due to --telnet flag
print("Telnet server should be running on port 8023")
print("This script will run for 5 seconds then exit")

-- Keep running for a bit
_PY.setTimeout(function()
    print("Script finished after 5 seconds")
end, 5000)
