-- Test if web server functions are available
print("Testing web server functions...")

-- List all available _PY functions
print("Available _PY functions:")
for name, func in pairs(_PY) do
    print("  " .. name .. ": " .. type(func))
end

-- Check specifically for web server functions
if _PY.start_web_server then
    print("✓ start_web_server is available")
else
    print("❌ start_web_server is NOT available")
end

if _PY.stop_web_server then
    print("✓ stop_web_server is available")
else
    print("❌ stop_web_server is NOT available")
end

if _PY.get_web_server_status then
    print("✓ get_web_server_status is available")
else
    print("❌ get_web_server_status is NOT available")
end
