-- tkhtmlview Integration Demo - Shows the enhanced HTML capabilities
-- Demonstrates full HTML/CSS support with tkhtmlview library

local nativeUI = require('native_ui')
local json = require('json')

print("🎨 tkhtmlview Enhanced HTML Demo")

if not nativeUI.isAvailable() then
    print("❌ Native UI not available")
    return
end

print("✅ Native UI available!")

-- Create JSON UI showcasing tkhtmlview capabilities
print("\n📝 Creating enhanced HTML labels with tkhtmlview...")

local tkhtmlviewDemo = json.encode({
    elements = {
        {
            type = "header",
            text = "tkhtmlview Enhanced HTML Demo",
            level = 1,
            id = "title"
        },
        {
            type = "label",
            text = "This demo shows the enhanced HTML capabilities with tkhtmlview library",
            id = "description"
        },
        {
            type = "separator",
            id = "sep1"
        },
        
        -- Row 1: Extended color palette
        {
            type = "row",
            id = "color_palette_row",
            elements = {
                {
                    type = "label",
                    text = "<span style='color: purple;'>Purple</span>",
                    html = true,
                    id = "purple_label"
                },
                {
                    type = "label",
                    text = "<span style='color: orange;'>Orange</span>",
                    html = true,
                    id = "orange_label"
                },
                {
                    type = "label",
                    text = "<span style='color: #FF1493;'>Hot Pink</span>",
                    html = true,
                    id = "hotpink_label"
                }
            }
        },
        
        {
            type = "separator",
            id = "sep2"
        },
        
        -- Row 2: Hex colors
        {
            type = "label",
            text = "Hex Colors: <span style='color: #FF5733;'>#FF5733</span> <span style='color: #33FF57;'>#33FF57</span> <span style='color: #3357FF;'>#3357FF</span>",
            html = true,
            id = "hex_colors"
        },
        
        {
            type = "separator",
            id = "sep3"
        },
        
        -- Row 3: RGB colors
        {
            type = "label",
            text = "RGB Colors: <span style='color: rgb(255, 87, 51);'>rgb(255,87,51)</span> <span style='color: rgb(51, 255, 87);'>rgb(51,255,87)</span>",
            html = true,
            id = "rgb_colors"
        },
        
        {
            type = "separator",
            id = "sep4"
        },
        
        -- Row 4: Background colors
        {
            type = "row",
            id = "background_row",
            elements = {
                {
                    type = "label",
                    text = "<span style='background-color: yellow; padding: 5px;'>Yellow BG</span>",
                    html = true,
                    id = "yellow_bg"
                },
                {
                    type = "label",
                    text = "<span style='background-color: lightblue; padding: 5px;'>Light Blue BG</span>",
                    html = true,
                    id = "lightblue_bg"
                },
                {
                    type = "label",
                    text = "<span style='background-color: lightgreen; padding: 5px;'>Light Green BG</span>",
                    html = true,
                    id = "lightgreen_bg"
                }
            }
        },
        
        {
            type = "separator",
            id = "sep5"
        },
        
        -- Row 5: Font sizes with CSS
        {
            type = "label",
            text = "<span style='font-size: 10px;'>10px</span> <span style='font-size: 14px;'>14px</span> <span style='font-size: 18px;'>18px</span> <span style='font-size: 24px;'>24px</span>",
            html = true,
            id = "font_sizes"
        },
        
        {
            type = "separator",
            id = "sep6"
        },
        
        -- Row 6: Advanced styling
        {
            type = "label",
            text = "<div style='border: 2px solid #333; padding: 10px; border-radius: 5px; background-color: #f0f0f0;'><strong>Styled Box:</strong> <em>This shows advanced CSS styling with borders, padding, and background!</em></div>",
            html = true,
            id = "styled_box"
        },
        
        {
            type = "separator",
            id = "sep7"
        },
        
        -- Control buttons for dynamic updates
        {
            type = "row",
            id = "control_row",
            elements = {
                {
                    type = "button",
                    text = "Random Colors",
                    action = "random_colors",
                    id = "random_btn"
                },
                {
                    type = "button",
                    text = "Gradient Effect",
                    action = "gradient",
                    id = "gradient_btn"
                },
                {
                    type = "button",
                    text = "Animation",
                    action = "animate",
                    id = "animate_btn"
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
            text = "<h3 style='color: #2c3e50;'>Dynamic Content Area</h3><p>Click buttons above to see advanced HTML features!</p>",
            html = true,
            id = "dynamic_content"
        },
        
        {
            type = "separator",
            id = "sep9"
        },
        
        -- Status display with rich formatting
        {
            type = "row",
            id = "status_display_row",
            elements = {
                {
                    type = "label",
                    text = "<strong>System Status:</strong>",
                    html = true,
                    id = "status_label"
                },
                {
                    type = "label",
                    text = "<span style='color: #27ae60; font-weight: bold;'>● ONLINE</span>",
                    html = true,
                    id = "status_indicator"
                },
                {
                    type = "label",
                    text = "<small style='color: #7f8c8d;'>Last updated: Now</small>",
                    html = true,
                    id = "status_time"
                }
            }
        }
    }
})

-- Create window from JSON
local window = nativeUI.createWindow("tkhtmlview Demo", 700, 650)
local ui = nativeUI.fromJSON(tkhtmlviewDemo)
window:setUI(ui)

-- Demo state
local animationCount = 0

-- Set up callbacks
print("\n📞 Setting up enhanced HTML callbacks...")

-- Random colors button
window:setCallback("random_btn", function(data)
    print("🎲 Generating random colors")
    
    -- Generate random hex colors
    local colors = {}
    for i = 1, 3 do
        local r = math.random(0, 255)
        local g = math.random(0, 255)
        local b = math.random(0, 255)
        colors[i] = string.format("#%02X%02X%02X", r, g, b)
    end
    
    -- Update hex colors display
    local hexText = string.format(
        "Random Hex: <span style='color: %s;'>%s</span> <span style='color: %s;'>%s</span> <span style='color: %s;'>%s</span>",
        colors[1], colors[1], colors[2], colors[2], colors[3], colors[3]
    )
    window:setText("hex_colors", hexText)
    
    -- Update dynamic content
    local dynamicText = string.format([[
        <h3 style='color: %s;'>Random Colors Generated!</h3>
        <div style='background: linear-gradient(45deg, %s, %s, %s); padding: 15px; color: white; text-shadow: 1px 1px 2px black;'>
            <strong>Gradient Background</strong><br>
            <small>Colors: %s, %s, %s</small>
        </div>
    ]], colors[1], colors[1], colors[2], colors[3], colors[1], colors[2], colors[3])
    
    window:setText("dynamic_content", dynamicText)
end)

-- Gradient effect button
window:setCallback("gradient_btn", function(data)
    print("🌈 Creating gradient effect")
    
    local gradientText = [[
        <h3 style='background: linear-gradient(45deg, #ff6b6b, #4ecdc4, #45b7d1, #f9ca24); 
                   -webkit-background-clip: text; color: transparent; font-size: 24px;'>
            Gradient Text Effect!
        </h3>
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 20px; border-radius: 10px; color: white; text-align: center;'>
            <h4>Beautiful Gradient Box</h4>
            <p>This demonstrates advanced CSS gradients and styling!</p>
        </div>
    ]]
    
    window:setText("dynamic_content", gradientText)
end)

-- Animation button
window:setCallback("animate_btn", function(data)
    print("✨ Starting animation effect")
    animationCount = animationCount + 1
    
    local animText = string.format([[
        <h3 style='color: #e74c3c;'>Animation Effect #%d</h3>
        <div style='border: 3px solid #3498db; padding: 15px; background-color: #ecf0f1; border-radius: 8px;'>
            <p style='font-size: 16px; color: #2c3e50;'>
                <strong>Animated Content:</strong> This content changes each time you click!
            </p>
            <div style='background-color: #f39c12; color: white; padding: 8px; border-radius: 4px; display: inline-block;'>
                Counter: <strong>%d</strong>
            </div>
        </div>
    ]], animationCount, animationCount)
    
    window:setText("dynamic_content", animText)
end)

-- Show the window
window:show()
print("✅ tkhtmlview Demo window created!")

-- Set up real-time updates with advanced styling
print("\n🔄 Setting up real-time advanced HTML updates...")

local updateCount = 0
setInterval(function()
    updateCount = updateCount + 1
    local timestamp = os.date("%H:%M:%S")
    
    -- Update status with rich formatting
    local statusColors = {"#27ae60", "#f39c12", "#e74c3c", "#3498db"}
    local statusTexts = {"● ONLINE", "● PROCESSING", "● MAINTENANCE", "● UPDATING"}
    local index = (updateCount % 4) + 1
    
    window:setText("status_indicator", string.format(
        "<span style='color: %s; font-weight: bold; text-shadow: 1px 1px 1px rgba(0,0,0,0.3);'>%s</span>",
        statusColors[index], statusTexts[index]
    ))
    
    -- Update timestamp with styling
    window:setText("status_time", string.format(
        "<small style='color: #7f8c8d; font-style: italic;'>Last updated: %s (#%d)</small>",
        timestamp, updateCount
    ))
    
    -- Cycle through different font size demonstrations
    if updateCount % 5 == 0 then
        local sizes = {10, 12, 14, 16, 18, 20, 24}
        local sizeText = ""
        for _, size in ipairs(sizes) do
            sizeText = sizeText .. string.format(
                "<span style='font-size: %dpx; color: hsl(%d, 70%%, 50%%);'>%dpx</span> ",
                size, (size * 10) % 360, size
            )
        end
        window:setText("font_sizes", sizeText)
    end
    
    print("🎨 Advanced HTML update #" .. updateCount)
end, 2000)

print("\n🎉 tkhtmlview Demo complete!")
print("\n✨ Enhanced HTML Features demonstrated:")
print("   🎨 Full color palette (named, hex, rgb, hsl)")
print("   📐 CSS font sizes and styling")
print("   🌈 Background colors and gradients")
print("   📦 Borders, padding, and advanced layouts")
print("   🔄 Dynamic content with rich formatting")
print("   ⚡ Real-time updates with complex styling")
print("\n💡 tkhtmlview provides:")
print("   📋 Full HTML/CSS support")
print("   🎯 Drop-in replacement for SimpleHTMLLabel")
print("   🚀 No limitations on colors or tags!")
print("   🔧 Easy integration with existing code")
