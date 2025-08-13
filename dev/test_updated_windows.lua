-- Test the updated window manager from within EPLua
print("=== Testing Updated Window Manager ===")

local engine = fibaro.plua

-- Test 1: Create first window  
print("1. Creating first QuickApp window...")
local success1 = engine.lib.createQuickAppWindow(
    1001, 
    "Test QA 1001", 
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
    print("2. Creating second QuickApp window...")
    local success2 = engine.lib.createQuickAppWindow(
        1002, 
        "Test QA 1002", 
        600, 
        400, 
        300, 
        200
    )
    print("Window 2 creation:", success2)
    
    -- Test 3: Try to reuse first window
    setTimeout(function()
        print("3. Trying to reuse first window...")
        local success3 = engine.lib.createQuickAppWindow(
            1001, 
            "Test QA 1001 Reuse", 
            700, 
            500, 
            400, 
            300
        )
        print("Window 3 creation (should reuse):", success3)
        
        print("=== Check Safari ===")
        print("You should see 2 separate Safari windows:")
        print("- One for QA 1001")
        print("- One for QA 1002")
        print("The third call should have reused window 1001")
    end, 3000)
end, 3000)
