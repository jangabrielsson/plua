-- Test script to verify no error messages appear when no QuickApps are available
print("Testing QuickApps tab with no QuickApps available")
print("1. Open web interface at http://localhost:8888/static/plua_main_page.html")
print("2. Click on QuickApps tab")
print("3. Verify it shows a blank tab instead of error messages")

-- Don't define any QuickApps or Fibaro support
-- The _PY.get_quickapps() function should either not exist or return empty data

local timer_count = 0
_PY.setTimeout(function()
    timer_count = timer_count + 1
    print(string.format("Timer %d - QuickApps tab should remain blank", timer_count))
    if timer_count >= 3 then
        print("Test complete - you can now check the QuickApps tab behavior")
    end
end, 2000)
