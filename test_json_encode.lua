--%%name:JSONEncodeTest
--%%type:com.fibaro.binarySwitch
--%% offline:true

function QuickApp:onInit()
  self:debug("Testing JSON encoding fix...")

  -- Test 1: Simple array
  local arr = {"b", "c"}
  self:debug("Array:", json.encode(arr))
  
  -- Test 2: Table with array (this should now work correctly)
  local tbl = {a = {"b", "c"}}
  self:debug("Table with array:", json.encode(tbl))
  
  -- Test 3: Nested arrays
  local nested = {a = {"b", "c"}, d = {"e", "f"}}
  self:debug("Nested arrays:", json.encode(nested))
  
  -- Test 4: Mixed types
  local mixed = {a = {"b", "c"}, num = 123, str = "hello"}
  self:debug("Mixed types:", json.encode(mixed))
  
  -- Test 5: Complex nested structure
  local complex = {
    users = {
      {name = "Alice", roles = {"admin", "user"}},
      {name = "Bob", roles = {"user"}}
    },
    settings = {enabled = true, options = {"a", "b", "c"}}
  }
  self:debug("Complex nested:", json.encode(complex))
  
  -- Test 6: Try _PY.to_json as well
  self:debug("_PY.to_json result:", _PY.to_json({a = {"b", "c"}}))
  
  self:debug("JSON encode fix test completed!")
end 