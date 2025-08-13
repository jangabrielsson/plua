-- Test cross-platform browser launching with webbrowser module

print("=== Testing Cross-Platform Browser Window Creation ===")

local engine = fibaro.plua

-- Test 1: Create first window
print("Creating first QuickApp window...")
local success1 = engine.lib.createQuickAppWindow(
    3001, 
    "Cross-Platform Test 1", 
    800, 
    600, 
    50, 
    50
)
print("Window 1 creation:", success1)

-- Test 2: Create second window with different URL
setTimeout(function()
    print("Creating second QuickApp window...")
    local success2 = engine.lib.createQuickAppWindow(
        3002, 
        "Cross-Platform Test 2", 
        900, 
        700, 
        150, 
        100
    )
    print("Window 2 creation:", success2)
    
    -- Test 3: Try to reuse first window
    setTimeout(function()
        print("Attempting to reuse first window...")
        local success3 = engine.lib.createQuickAppWindow(
            3001, 
            "Reuse Test", 
            600, 
            400, 
            200, 
            200
        )
        print("Window 1 reuse:", success3)
        
        print("=== Cross-platform browser test completed! ===")
        print("Windows should open in the default system browser")
        print("Window reuse should work for same QA IDs")
    end, 3000)
end, 3000)
