-- Test Safari window behavior with explicit window creation
local engine = fibaro.plua

print("=== Testing Safari Window Creation ===")

-- Test 1: Create first window for QA 2001
print("Creating window for QA 2001...")
local success1 = engine.lib.createQuickAppWindow(2001, "QA 2001 Window", 500, 400, 100, 100)
print("QA 2001 window creation:", success1)

-- Wait a moment to let Safari open
setTimeout(function()
    -- Test 2: Create second window for QA 2002 (different URL)
    print("Creating window for QA 2002...")
    local success2 = engine.lib.createQuickAppWindow(2002, "QA 2002 Window", 600, 500, 200, 150)
    print("QA 2002 window creation:", success2)
    
    setTimeout(function()
        -- Test 3: Try to create another window for QA 2001 (should reuse)
        print("Trying to reuse window for QA 2001...")
        local success3 = engine.lib.createQuickAppWindow(2001, "QA 2001 Reuse", 400, 300, 300, 200)
        print("QA 2001 window reuse:", success3)
        
        setTimeout(function()
            -- Test 4: Try to create another window for QA 2002 (should reuse)
            print("Trying to reuse window for QA 2002...")
            local success4 = engine.lib.createQuickAppWindow(2002, "QA 2002 Reuse", 700, 600, 400, 250)
            print("QA 2002 window reuse:", success4)
            
            print("=== Safari window test completed! ===")
            print("Expected: 2 separate Safari windows (one for each QA)")
            print("Actual windows should reuse for same QA IDs")
        end, 2000)
    end, 2000)
end, 2000)
