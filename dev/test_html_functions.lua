-- Test HTML functions
print("=== Testing HTML Functions ===")

-- Test html2console function
local html_text = "<font color='red'>Error:</font> Something went wrong<br><font color='green'>Success:</font> Operation completed"
local console_text = _PY.html2console(html_text)
print("Original HTML:", html_text)
print("Console output:", console_text)

-- Test get_available_colors function
local colors = _PY.get_available_colors()
print("\nAvailable colors:")
for i, color in ipairs(colors) do
    print(string.format("  %d: %s", i, color))
end

-- Test with nested tags
local nested_html = "<font color='blue'>Outer <font color='yellow'>nested</font> text</font>"
local nested_console = _PY.html2console(nested_html)
print("\nNested HTML:", nested_html)
print("Nested console:", nested_console)

print("\n=== HTML Functions Test Complete ===")
