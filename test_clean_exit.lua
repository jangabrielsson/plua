print("Test run - creating window for QA 4123...")
_PY.open_quickapp_window(4123, "Test Window", 400, 300, 100, 100)
print("Window created, script will exit in 2 seconds")

setTimeout(function()
    print("Script exiting cleanly...")
    os.exit(0)
end, 2000)
