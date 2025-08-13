-- Working HTML Demo - Using current SimpleHTMLLabel with proper features
-- Shows what actually works reliably with the current HTML system

local nativeUI = require('native_ui')
local json = require('json')

print("🎨 Working HTML Demo")

if not nativeUI.isAvailable() then
    print("❌ Native UI not available")
    return
end

print("✅ Native UI available!")

-- Create JSON UI with WORKING HTML features only
print("\n📝 Creating working HTML labels...")

local workingHtmlDemo = json.encode({
    elements = {
        {
            type = "header",
            text = "Working HTML Demo",
            level = 1,
            id = "title"
        },
        {
            type = "label",
            text = "This demo shows HTML features that actually work reliably",
            id = "description"
        },
        {
            type = "separator",
            id = "sep1"
        },
        
        -- Row 1: Working text formatting
        {
            type = "row",
            id = "text_format_row",
            elements = {
                {
                    type = "label",
                    text = "<b>Bold Text</b>",
                    html = true,
                    id = "bold_label"
                },
                {
                    type = "label",
                    text = "<i>Italic Text</i>",
                    html = true,
                    id = "italic_label"
                },
                {
                    type = "label",
                    text = "<u>Underlined</u>",
                    html = true,
                    id = "underline_label"
                }
            }
        },
        
        {
            type = "separator",
            id = "sep2"
        },
        
        -- Row 2: Working colors (only the 3 supported ones)
        {
            type = "row",
            id = "color_row",
            elements = {
                {
                    type = "label",
                    text = "<font color=\"red\">Red Text</font>",
                    html = true,
                    id = "red_label"
                },
                {
                    type = "label",
                    text = "<font color=\"blue\">Blue Text</font>",
                    html = true,
                    id = "blue_label"
                },
                {
                    type = "label",
                    text = "<font color=\"green\">Green Text</font>",
                    html = true,
                    id = "green_label"
                }
            }
        },
        
        {
            type = "separator",
            id = "sep3"
        },
        
        -- Row 3: Working font sizes
        {
            type = "row",
            id = "size_row",
            elements = {
                {
                    type = "label",
                    text = "<small>Small Text</small>",
                    html = true,
                    id = "small_label"
                },
                {
                    type = "label",
                    text = "Normal Text",
                    id = "normal_label"
                },
                {
                    type = "label",
                    text = "<big>Big Text</big>",
                    html = true,
                    id = "big_label"
                }
            }
        },
        
        {
            type = "separator",
            id = "sep4"
        },
        
        -- Row 4: Working alignment (added in our fixes)
        {
            type = "label",
            text = "<center><b>Centered Bold Text</b></center>",
            html = true,
            id = "center_label"
        },
        
        {
            type = "label",
            text = "<right><i>Right-aligned Italic</i></right>",
            html = true,
            id = "right_label"
        },
        
        {
            type = "separator",
            id = "sep5"
        },
        
        -- Row 5: Combined formatting that works
        {
            type = "label",
            text = "<center><big><font color=\"blue\"><b>Big Blue Bold Centered</b></font></big></center>",
            html = true,
            id = "combined_label"
        },
        
        {
            type = "separator",
            id = "sep6"
        },
        
        -- Row 6: Multi-line with line breaks
        {
            type = "label",
            text = "<b>Status Report:</b><br><font color=\"green\">✓ System Online</font><br><font color=\"blue\">ℹ All systems operational</font>",
            html = true,
            id = "status_report"
        },
        
        {
            type = "separator",
            id = "sep7"
        },
        
        -- Control buttons
        {
            type = "row",
            id = "control_row",
            elements = {
                {
                    type = "button",
                    text = "Update Colors",
                    action = "update_colors",
                    id = "update_btn"
                },
                {
                    type = "button",
                    text = "Change Size",
                    action = "change_size",
                    id = "size_btn"
                },
                {
                    type = "button",
                    text = "Toggle Alignment",
                    action = "toggle_align",
                    id = "align_btn"
                }
            }
        },
        
        {
            type = "separator",
            id = "sep8"
        },
        
        -- Dynamic content area
        {
            type = "label",
            text = "<center><b>Dynamic Content</b><br><i>Click buttons above to see updates</i></center>",
            html = true,
            id = "dynamic_content"
        },
        
        {
            type = "separator",
            id = "sep9"
        },
        
        -- Status display (no real-time updates to avoid threading issues)
        {
            type = "row",
            id = "status_row",
            elements = {
                {
                    type = "label",
                    text = "<b>System:</b>",
                    html = true,
                    id = "system_label"
                },
                {
                    type = "label",
                    text = "<font color=\"green\">● READY</font>",
                    html = true,
                    id = "status_indicator"
                },
                {
                    type = "label",
                    text = "<small>HTML Working</small>",
                    html = true,
                    id = "status_text"
                }
            }
        }
    }
})

-- Create window from JSON
local window = nativeUI.createWindow("Working HTML Demo", 600, 550)
local ui = nativeUI.fromJSON(workingHtmlDemo)
window:setUI(ui)

-- Demo state
local colorIndex = 1
local sizeIndex = 1
local alignIndex = 1

-- Set up callbacks (no real-time updates to avoid threading issues)
print("\n📞 Setting up working HTML callbacks...")

-- Update colors button
window:setCallback("update_btn", function(data)
    print("🎨 Updating colors")
    
    local colors = {"red", "blue", "green"}
    colorIndex = (colorIndex % 3) + 1
    local color = colors[colorIndex]
    
    -- Update the combined label with new color
    local combinedText = string.format(
        "<center><big><font color=\"%s\"><b>Big %s Bold Centered</b></font></big></center>",
        color, color:gsub("^%l", string.upper)
    )
    window:setText("combined_label", combinedText)
    
    -- Update dynamic content
    local dynamicText = string.format(
        "<center><b>Color Updated!</b><br><font color=\"%s\">Now using %s color</font></center>",
        color, color
    )
    window:setText("dynamic_content", dynamicText)
    
    -- Update status
    window:setText("status_indicator", string.format("<font color=\"%s\">● %s</font>", color, color:upper()))
end)

-- Change size button
window:setCallback("size_btn", function(data)
    print("📏 Changing size")
    
    local sizes = {"small", "normal", "big"}
    local sizeTags = {"<small>%s</small>", "%s", "<big>%s</big>"}
    sizeIndex = (sizeIndex % 3) + 1
    
    local sizeTag = sizeTags[sizeIndex]
    local sizeName = sizes[sizeIndex]
    
    -- Update dynamic content with new size
    local dynamicText = string.format(
        "<center>" .. sizeTag .. "</center>",
        "<b>Size Changed!</b><br><i>Now using " .. sizeName .. " size</i>"
    )
    window:setText("dynamic_content", dynamicText)
    
    -- Update status
    window:setText("status_text", string.format("<small>Size: %s</small>", sizeName))
end)

-- Toggle alignment button
window:setCallback("align_btn", function(data)
    print("📐 Toggling alignment")
    
    local alignments = {"left", "center", "right"}
    local alignNames = {"Left", "Center", "Right"}
    alignIndex = (alignIndex % 3) + 1
    
    local align = alignments[alignIndex]
    local alignName = alignNames[alignIndex]
    
    -- Update dynamic content with new alignment
    local dynamicText = string.format(
        "<%s><b>Alignment Changed!</b><br><i>Now %s-aligned</i></%s>",
        align, alignName:lower(), align
    )
    window:setText("dynamic_content", dynamicText)
    
    -- Update status
    window:setText("status_text", string.format("<small>Align: %s</small>", alignName))
end)

-- Show the window
window:show()
print("✅ Working HTML Demo window created!")

print("\n🎉 Working HTML Demo complete!")
print("\n✅ Features that work reliably:")
print("   🔤 <b>, <strong>, <i>, <em>, <u> - Text formatting")
print("   📏 <big>, <small> - Font sizes")
print("   🎨 <font color=\"red/blue/green\"> - Three colors")
print("   📐 <center>, <left>, <right> - Text alignment")
print("   📄 <br> - Line breaks")
print("   🔄 Dynamic content updates via setText()")
print("   🎛️ Mixed HTML and regular labels in rows")
print("\n💡 This demo shows what actually works without issues!")
print("📋 No threading problems, no unsupported colors, no crashes!")
