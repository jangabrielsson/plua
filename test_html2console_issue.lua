-- Test html2console issue with &lt; characters
print("Testing html2console with &lt; characters:")
print("=" .. string.rep("=", 50))

-- Test cases that should work but don't
local test_cases = {
    "Hello &lt;world&gt;",  -- Should become "Hello <world>"
    "Text with &lt; and &gt;",  -- Should become "Text with < and >"
    "&lt;not a tag&gt;",  -- Should become "<not a tag>"
    "Normal text &lt; more text",  -- Should become "Normal text < more text"
    "&lt;font color='red'&gt;Red text&lt;/font&gt;",  -- Should become colored text
    "<font color='red'>lkjklj < jkjdsf</font>",  -- Should become "lkjklj < jkjdsf" in red
}

for i, test in ipairs(test_cases) do
    print("Test " .. i .. ": " .. test)
    print("Result: " .. _PY.html2console(test))
    print()
end

print("Expected behavior:")
print("Test 1 should show: Hello <world>")
print("Test 2 should show: Text with < and >")
print("Test 3 should show: <not a tag>")
print("Test 4 should show: Normal text < more text")
print("Test 5 should show: Red text (in red color)")
print("Test 6 should show: lkjklj < jkjdsf (in red color)") 