-- Test script for graceful shutdown
print("Starting graceful shutdown test")
print("Open the web interface at http://localhost:8888/static/plua_main_page.html")
print("Navigate to the QuickApps tab to establish WebSocket connection")
print("Then type exit() to test graceful shutdown")

-- Simple timer to keep things active
_PY.setTimeout(function()
    print("Timer executed - WebSocket should be working")
end, 2000)
