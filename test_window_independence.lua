-- Test script that creates a window and exits quickly
print("=== Window Independence Test ===")
print("Creating desktop window...")

-- Explicitly create desktop window
_PY.open_quickapp_window(9999, "Independence Test", 600, 400, 200, 200)

-- Wait just a moment for window to be created
setTimeout(function()
    print("Window should be created. Script will now exit.")
    print("The window should remain open and functional.")
    -- Don't call os.exit() - let the script end naturally
end, 1000)

-- Also set a timeout to ensure script doesn't hang
setTimeout(function()
    print("Forcing script exit after 3 seconds")
    os.exit(0)  -- Force exit if still hanging
end, 3000)

print("Script setup complete. Window should be opening...")
