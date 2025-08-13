-- EPLua Native UI Button Row Demo with Working Callbacks
-- Uses direct _PY API to demonstrate button row functionality with callbacks

print("🎛️ EPLua Native UI Demo (Button Row Demo - Working Callbacks)")

-- Check if native UI is available
if not _PY.isNativeUIAvailable() then
    print("❌ Native UI not available")
    return
end

print("✅ Native UI available!")
print("\n📝 Creating QuickApp-style window...")

-- Create window
local window = _PY.createNativeWindow("QuickApp Button Row Demo", 600, 500)

-- UI definition with various button row configurations
local ui = {
    {
        type = "label",
        id = "title",
        text = "🎛️ EPLua Button Row Demo",
        style = { fontSize = "18px", fontWeight = "bold", textAlign = "center", marginBottom = "20px" }
    },
    {
        type = "separator"
    },
    {
        type = "label",
        id = "status",
        text = "✨ Callbacks enabled! Try clicking buttons.",
        style = { color = "green", marginBottom = "15px" }
    },
    {
        type = "separator"
    },
    {
        type = "label",
        text = "4-Button Action Row:",
        style = { fontWeight = "bold", marginBottom = "5px" }
    },
    {
        type = "button_row",
        buttons = {
            {text = "📊 Btn 1", id = "btn1", style = {backgroundColor = "#e3f2fd"}},
            {text = "🔧 Btn 2", id = "btn2"},
            {text = "📝 Btn 3", id = "btn3"},
            {text = "🎯 Btn 5", id = "btn5", style = {backgroundColor = "#fff3e0"}}
        }
    },
    {
        type = "separator"
    },
    {
        type = "label",
        text = "2-Button Row:",
        style = { fontWeight = "bold", marginBottom = "5px" }
    },
    {
        type = "button_row",
        buttons = {
            {text = "💾 Save", id = "save", style = {backgroundColor = "#c8e6c9"}},
            {text = "❌ Cancel", id = "cancel", style = {backgroundColor = "#ffcdd2"}}
        }
    },
    {
        type = "separator"
    },
    {
        type = "label",
        text = "3-Button Mixed Styles:",
        style = { fontWeight = "bold", marginBottom = "5px" }
    },
    {
        type = "button_row",
        buttons = {
            {text = "🔸 Normal", id = "normal"},
            {text = "⭐ Primary", id = "primary", style = {backgroundColor = "#1976d2", color = "white", fontWeight = "bold"}},
            {text = "🔸 Alt", id = "alt"}
        }
    },
    {
        type = "separator"
    },
    {
        type = "label",
        text = "5-Button Row:",
        style = { fontWeight = "bold", marginBottom = "5px" }
    },
    {
        type = "button_row",
        buttons = {
            {text = "A", id = "btnA", style = {backgroundColor = "#f8bbd9"}},
            {text = "B", id = "btnB", style = {backgroundColor = "#e1bee7"}},
            {text = "C", id = "btnC", style = {backgroundColor = "#c5cae9"}},
            {text = "D", id = "btnD", style = {backgroundColor = "#bbdefb"}},
            {text = "E", id = "btnE", style = {backgroundColor = "#b2dfdb"}}
        }
    }
}

-- Set the UI
_PY.setNativeUI(window.window_id, ui)

-- Set up callbacks for the buttons
local function setupCallbacks()
    local buttons = {"btn1", "btn2", "btn3", "btn5", "save", "cancel", "normal", "primary", "alt", "btnA", "btnB", "btnC", "btnD", "btnE"}
    
    for _, btnId in ipairs(buttons) do
        local success = _PY.setNativeCallback(window.window_id, btnId, function(data)
            print(string.format("🎯 Button '%s' clicked! Data: %s", btnId, data and data.value or "nil"))
            
            -- Update status label to show which button was clicked
            _PY.setNativeValue(window.window_id, "status", string.format("🎯 Last clicked: %s", btnId))
        end)
        
        if not success then
            print(string.format("⚠️ Failed to set callback for button: %s", btnId))
        end
    end
end

-- Setup callbacks
setupCallbacks()

-- Show the window
_PY.showNativeWindow(window.window_id)

print("✅ QuickApp window created and displayed!")
print("📝 Window ID:", window.window_id)
print("\n🎉 Button Row Demo complete!")
print("💡 Window shows various button row configurations:")
print("   🔸 4-button action row (Btn 1, Btn 2, Btn 3, Btn 5)")
print("   🔸 2-button row (Save, Cancel)")
print("   🔸 3-button mixed styles row (Primary highlighted)")
print("   🔸 5-button row (A, B, C, D, E)")
print("🎛️ This demonstrates horizontal button layout with working callbacks!")
print("\n💡 Click any button to see callback functionality!")

setInterval(function() end,1000)