--%%name:PositionTest
--%%type:com.fibaro.binarySwitch
--%%desktop:false

function QuickApp:onInit()
  self:debug("onInit - Testing window positioning")
  
  -- Get screen dimensions
  local screen = _PY.get_screen_dimensions()
  print("Screen dimensions:", json.encode(screen))
  
  -- Calculate positions for multiple windows
  local window_width, window_height = 400, 300
  
  -- Top-left corner
  local result1 = _PY.open_quickapp_window(self.id + 1, "Top-Left Window", window_width, window_height, 50, 50)
  print("Top-left window:", json.encode(result1))
  
  -- Top-right corner
  if screen.success then
    local x = screen.width - window_width - 50
    local result2 = _PY.open_quickapp_window(self.id + 2, "Top-Right Window", window_width, window_height, x, 50)
    print("Top-right window:", json.encode(result2))
    
    -- Center screen
    local center_x = (screen.width - window_width) // 2
    local center_y = (screen.height - window_height) // 2
    local result3 = _PY.open_quickapp_window(self.id + 3, "Centered Window", window_width, window_height, center_x, center_y)
    print("Centered window:", json.encode(result3))
  end
  
  -- Default positioning (let plua decide)
  local result4 = _PY.open_quickapp_window(self.id + 4, "Default Position Window", window_width, window_height)
  print("Default window:", json.encode(result4))
end
