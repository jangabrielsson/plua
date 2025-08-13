-- Test script to verify window reuse behavior with multiple QuickApps

-- Simulate creating multiple QAs with different URLs
local engine = fibaro.plua

-- Test 1: Create window for QA 1001
local success1 = engine.lib.createQuickAppWindow(
    1001,
    "QA 1001 Window",
    500,
    400,
    100,
    100
)
print("QA 1001 window creation:", success1)

-- Test 2: Create window for QA 1002 (different URL)
local success2 = engine.lib.createQuickAppWindow(
    1002,
    "QA 1002 Window", 
    600,
    500,
    200,
    150
)
print("QA 1002 window creation:", success2)

-- Test 3: Try to create another window for QA 1001 (should reuse)
local success3 = engine.lib.createQuickAppWindow(
    1001,
    "QA 1001 Reuse Test",
    400,
    300,
    300,
    200
)
print("QA 1001 window reuse:", success3)

-- Test 4: Try to create another window for QA 1002 (should reuse)
local success4 = engine.lib.createQuickAppWindow(
    1002,
    "QA 1002 Reuse Test",
    700,
    600,
    400,
    250
)
print("QA 1002 window reuse:", success4)

print("Window behavior test completed!")
