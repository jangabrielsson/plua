--%%name:UItest
--%%type:com.fibaro.multilevelSwitch
--%%debug:false
--%%offline:true

--%%u:{label="lbl1",text="Hello World"}
--%%u:{{button="btn1",text="Test Update",visible=true,onReleased="testUpdate"}}

function QuickApp:testUpdate(ev)
  print("testUpdate called")
  
  -- Check if broadcast function exists
  if _PY.broadcast_ui_update then
    print("broadcast_ui_update function exists")
  else
    print("ERROR: broadcast_ui_update function not found!")
    return
  end
  
  -- Update the label
  local newText = "Updated at " .. os.date("%H:%M:%S")
  print("Updating label to:", newText)
  
  local emulator = fibaro.plua
  if emulator and emulator.updateView then
    emulator:updateView(self.id, {
      componentName = "lbl1", 
      propertyName = "text", 
      newValue = newText
    })
    print("updateView called successfully")
  else
    print("ERROR: emulator or updateView not available")
  end
end

function QuickApp:onInit()
  self:debug("onInit")
  print("QuickApp initialized with ID:", self.id)
  
  -- Test the broadcast function
  if _PY.broadcast_ui_update then
    print("broadcast_ui_update function is available")
  else
    print("WARNING: broadcast_ui_update function not available")
  end
end
