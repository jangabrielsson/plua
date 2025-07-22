--%%name:WSDebugTest
--%%type:com.fibaro.multilevelSwitch
--%%debug:false
--%%offline:true

--%%u:{label="lbl1",text="Initial Text"}
--%%u:{{button="testBtn",text="Update & Debug",visible=true,onReleased="testWSUpdate"}}

function QuickApp:testWSUpdate(ev)
  print("=== WebSocket Update Test ===")
  
  -- 1. Check if broadcast function exists
  if _PY.broadcast_ui_update then
    print("✓ broadcast_ui_update function exists")
  else
    print("✗ broadcast_ui_update function NOT found!")
    return
  end
  
  -- 2. Update the label text
  local timestamp = os.date("%H:%M:%S")
  local newText = "Updated at " .. timestamp
  print("Updating label to:", newText)
  
  -- 3. Update the view through emulator
  local emulator = fibaro.plua
  if emulator and emulator.updateView then
    print("✓ Calling emulator:updateView")
    emulator:updateView(self.id, {
      componentName = "lbl1", 
      propertyName = "text", 
      newValue = newText
    })
    print("✓ updateView completed")
  else
    print("✗ emulator or updateView not available")
    return
  end
  
  -- 4. Test broadcast directly
  print("✓ Calling _PY.broadcast_ui_update(" .. self.id .. ")")
  _PY.broadcast_ui_update(self.id)
  print("✓ Broadcast call completed")
  
  -- 5. Wait and try again to see if there's any delay
  setTimeout(function()
    print("=== Second broadcast attempt ===")
    _PY.broadcast_ui_update(self.id)
    print("✓ Second broadcast completed")
  end, 1000)
  
  print("=== Test completed ===")
end

function QuickApp:onInit()
  self:debug("onInit")
  print("WebSocket Debug QuickApp initialized")
  print("QuickApp ID:", self.id)
  print("Available functions:")
  print("  - broadcast_ui_update:", _PY.broadcast_ui_update and "YES" or "NO")
  print("  - get_quickapp:", _PY.get_quickapp and "YES" or "NO")
  print("  - get_quickapps:", _PY.get_quickapps and "YES" or "NO")
end
