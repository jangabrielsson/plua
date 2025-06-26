
-- _PY.mainHook = function(filename)
--   -- Read the file content
--   local file = io.open(filename, "r")
--   local content = file:read("*all")
--   file:close()
  
--   -- Do preprocessing for Fibaro environment
--   local preprocessed = preprocess_for_fibaro(content)
  
--   -- Load and execute the preprocessed content
--   local func, err = load(preprocessed, filename)
--   if func then
--       func()
--       return true
--   else
--       return false
--   end
-- end