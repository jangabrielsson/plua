-- Test the updated window manager using direct _PY calls
print("=== Testing Updated Window Manager (Direct _PY calls) ===")

-- Test 1: Create first window
print("1. Creating first browser window...")
local success1 = _PY.create_browser_window(
    "test_window_1", 
    "http://localhost:8080/static/quickapp_ui.html?qa_id=1001&desktop=true",
    600, 
    400, 
    100, 
    100
)
print("Window 1 creation:", success1)

-- Wait a bit
_PY.sleep(3)

-- Test 2: Create second window
setTimeout(function()
    print("2. Creating second browser window...")
    local success2 = _PY.create_browser_window(
        "test_window_2", 
        "http://localhost:8080/static/quickapp_ui.html?qa_id=1002&desktop=true",
        600, 
        400, 
        300, 
        200
    )
    print("Window 2 creation:", success2)
    
    -- Test 3: Try to reuse first window
    setTimeout(function()
        print("3. Trying to reuse first window...")
        local success3 = _PY.create_browser_window(
            "test_window_1",  -- Same window ID
            "http://localhost:8080/static/quickapp_ui.html?qa_id=1001&desktop=true",
            700, 
            500, 
            400, 
            300
        )
        print("Window 3 creation (should reuse):", success3)
        
        -- List windows
        setTimeout(function()
            print("4. Listing all windows:")
            local windows = _PY.list_browser_windows()
            if windows then
                for window_id, info in pairs(windows) do
                    print(string.format("  %s: %s (%dx%d)", window_id, info.url, info.width, info.height))
                end
            end
            
            print("=== Check Safari ===")
            print("You should see 2 separate Safari windows:")
            print("- Window 1: QA 1001")
            print("- Window 2: QA 1002")
            print("The third call should have reused window 1")
        end, 2000)
    end, 3000)
end, 3000)
