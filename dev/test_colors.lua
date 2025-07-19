-- Test color output with ANSI codes
print("Testing HTML color conversion...")

-- Test visible color output
local html = 'This is <font color="red">RED TEXT</font> and <font color="blue">BLUE TEXT</font> and <font color="green">GREEN TEXT</font>!'
local colored_output = _PY.html2console(html)

print("Original HTML:")
print(html)
print("\nColored output:")
print(colored_output)

-- Test multiple colors
print("\nTesting various colors:")
local colors_to_test = {"red", "green", "blue", "yellow", "magenta", "cyan", "orange", "purple"}
for i, color in ipairs(colors_to_test) do
    local test_html = '<font color="' .. color .. '">' .. color .. ' text</font>'
    local result = _PY.html2console(test_html)
    print(result)
end

print("\nColor test completed!")
