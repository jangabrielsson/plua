# Window Background Color Control

PLua now supports setting the background color of QuickApp browser windows through the new `_PY.set_window_background()` function.

## Function Signature

```lua
_PY.set_window_background(windowID, color) -> boolean
```

### Parameters

- **windowID** (string): The window ID in the format "quickapp_" + QuickApp ID
- **color** (string): Color specification in one of these formats:
  - Web color name: "red", "blue", "lightgreen", "pink", etc.
  - RGB string: "255,100,50" (red, green, blue values 0-255)

### Returns

- **boolean**: `true` if the background was set successfully, `false` otherwise

## Usage Examples

### Basic Usage

```lua
-- Set background to a named color
_PY.set_window_background("quickapp_5555", "lightblue")

-- Set background using RGB values
_PY.set_window_background("quickapp_5555", "255,220,220")

-- Set background to white
_PY.set_window_background("quickapp_5555", "white")
```

### In a QuickApp

```lua
--%%name:ColorfulQA
--%%type:com.fibaro.binarySwitch
--%%desktop:true
--%%u:{button="red_bg",text="Red Background",onReleased="setRedBackground"}
--%%u:{button="green_bg",text="Green Background",onReleased="setGreenBackground"}
--%%u:{button="custom_bg",text="Custom RGB",onReleased="setCustomBackground"}

function QuickApp:onInit()
    self:debug("Colorful QuickApp initialized")
    -- Set initial background color
    self:setBackground("lightgray")
end

function QuickApp:setBackground(color)
    local windowId = "quickapp_" .. self.id
    local success = _PY.set_window_background(windowId, color)
    if success then
        self:debug("Background set to: " .. color)
    else
        self:warning("Failed to set background to: " .. color)
    end
    return success
end

function QuickApp:setRedBackground()
    self:setBackground("lightcoral")
end

function QuickApp:setGreenBackground()
    self:setBackground("lightgreen")
end

function QuickApp:setCustomBackground()
    -- Set a custom purple using RGB
    self:setBackground("200,150,255")
end
```

### Using the Convenience Function

PLua also provides a convenience function through the emulator library:

```lua
-- Using the convenience function (automatically constructs window ID)
Emu.lib.setQuickAppWindowBackground(5555, "lightblue")

-- This is equivalent to:
_PY.set_window_background("quickapp_5555", "lightblue")
```

## Supported Colors

### Named Colors
- Standard CSS color names: "red", "blue", "green", "yellow", "purple", etc.
- Extended colors: "lightblue", "darkgreen", "lightcoral", "lavender", etc.

### RGB Format
- Format: "R,G,B" where R, G, B are integers from 0-255
- Examples: "255,0,0" (red), "0,255,0" (green), "100,150,200" (light blue)

## Technical Notes

- The function targets the UI tab of QuickApp windows specifically
- Uses CSS injection via AppleScript on macOS (Safari)
- The background color change is applied with `!important` CSS priority
- Changes are immediate and don't require window refresh
- Currently supported on macOS with Safari browser

## Platform Support

- ✅ macOS (Safari) - Full support with AppleScript injection
- ❌ Windows/Linux - Not yet implemented (planned for future releases)
