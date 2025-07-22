-- Test script for granular UI updates
print("Testing granular UI updates...")

-- Create device info for QuickApp
local device = {
    id = 5555,
    name = "GranularTest",
    type = "com.fibaro.genericDevice"
}

-- Set up UI
local UI = {
    {id = 1, type = "label", text = "Initial label text", row = 1, visible = true},
    {id = 2, type = "button", text = "Click me", row = 2, visible = true},
    {id = 3, type = "slider", value = 50, min = 0, max = 100, row = 3, visible = true}
}

-- Create QuickApp instance  
local qa = QuickApp(device)
qa.UI = UI

-- Function to test different types of granular updates
local function testGranularUpdates()
    print("Starting granular update tests...")
    
    -- Update label text every 2 seconds
    setTimeout(function()
        print("Updating label text...")
        qa:updateView(1, "text", "Updated label text at " .. os.date("%H:%M:%S"))
    end, 2000)
    
    -- Update slider value every 3 seconds
    setTimeout(function()
        print("Updating slider value...")
        local newValue = math.random(0, 100)
        qa:updateView(3, "value", newValue)
    end, 3000)
    
    -- Update button text every 4 seconds
    setTimeout(function()
        print("Updating button text...")
        qa:updateView(2, "text", "Updated at " .. os.date("%H:%M:%S"))
    end, 4000)
    
    -- Repeat the test cycle
    setTimeout(function()
        testGranularUpdates()
    end, 5000)
end

-- Start testing after 1 second
setTimeout(testGranularUpdates, 1000)

-- Keep the script running
print("Test script is running. Check the web interface for granular updates!")
