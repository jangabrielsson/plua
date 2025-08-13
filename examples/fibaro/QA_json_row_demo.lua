--%%name:JSON_Row_Demo
--%%type:com.fibaro.binarySwitch
--%%save:dev/json_row_demo.fqa
--%% proxy:true
--%%project:888
--%%desktop:true
--%%offline:true

-- Simple JSON UI with Row Demo
-- This demo shows how to create UI with rows containing different elements

-- Single label row
--%%u:{label="status_label",text="JSON Row Demo - Ready"}

-- Button row with multiple buttons
--%%u:{{button="btn1",text="Action 1",visible=true,onReleased="action1"},{button="btn2",text="Action 2",visible=true,onReleased="action2"},{button="btn3",text="Reset",visible=true,onReleased="reset"}}

-- Mixed row with slider and switch
--%%u:{{slider="level_slider",text="Level",min="0",max="100",value="50",visible=true,onChanged="levelChanged"},{switch="enable_switch",text="Enable",value="true",visible=true,onReleased="toggleEnable"}}

-- Dropdown selection row
--%%u:{select="mode_select",text="Mode",visible=true,onToggled="modeChanged",value="1",options={{type="option",text="Auto",value="1"},{type="option",text="Manual",value="2"},{type="option",text="Off",value="3"}}}

-- Multi-select row
--%%u:{multi="features_multi",text="Features",visible=true,values={"1","3"},onToggled="featuresChanged",options={{type="option",text="Logging",value="1"},{type="option",text="Alerts",value="2"},{type="option",text="Backup",value="3"}}}

-- Status display row
--%%u:{{label="temp_label",text="Temperature: 22°C"},{label="humidity_label",text="Humidity: 45%"}}

local json = require('json')

function QuickApp:onInit()
  self:debug("JSON Row Demo initialized")
  self:updateProperty("value", false)
  
  -- Update status every few seconds to show dynamic updates
  setInterval(function()
    local temp = math.random(18, 28)
    local humidity = math.random(35, 65)
    self:updateView("temp_label", "text", "Temperature: " .. temp .. "°C")
    self:updateView("humidity_label", "text", "Humidity: " .. humidity .. "%")
    
    -- Update main status
    local time = os.date("%H:%M:%S")
    self:updateView("status_label", "text", "JSON Row Demo - Active " .. time)
  end, 3000)
end

-- Button row handlers
function QuickApp:action1(ev)
  self:debug("Action 1 pressed")
  self:updateProperty("value", true)
  self:updateView("status_label", "text", "Action 1 executed!")
end

function QuickApp:action2(ev)
  self:debug("Action 2 pressed")
  self:updateProperty("value", false)
  self:updateView("status_label", "text", "Action 2 executed!")
end

function QuickApp:reset(ev)
  self:debug("Reset pressed")
  self:updateProperty("value", false)
  -- Reset slider to middle
  self:updateView("level_slider", "value", "50")
  -- Reset switch to on
  self:updateView("enable_switch", "value", "true")
  self:updateView("status_label", "text", "System reset!")
end

-- Mixed row handlers
function QuickApp:levelChanged(ev)
  local level = ev.values[1]
  self:debug("Level changed to: " .. level)
  self:updateView("status_label", "text", "Level set to " .. level .. "%")
end

function QuickApp:toggleEnable(ev)
  local enabled = ev.values[1]
  self:debug("Enable toggled to: " .. enabled)
  self:updateView("status_label", "text", "Enable: " .. (enabled == "true" and "ON" or "OFF"))
end

-- Selection handlers
function QuickApp:modeChanged(ev)
  local mode = ev.values[1]
  local modes = {"Auto", "Manual", "Off"}
  local modeName = modes[tonumber(mode)] or "Unknown"
  self:debug("Mode changed to: " .. modeName)
  self:updateView("status_label", "text", "Mode: " .. modeName)
end

function QuickApp:featuresChanged(ev)
  local features = ev.values[1]
  self:debug("Features changed: " .. json.encode(features))
  local count = #features
  self:updateView("status_label", "text", count .. " features selected")
end

-- Device interface methods
function QuickApp:turnOn()
  self:debug("Turning on")
  self:updateProperty("value", true)
  self:updateView("status_label", "text", "Device turned ON")
end

function QuickApp:turnOff()
  self:debug("Turning off")
  self:updateProperty("value", false)
  self:updateView("status_label", "text", "Device turned OFF")
end
