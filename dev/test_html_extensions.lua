-- Test HTML extension functions
print("Testing HTML extension functions...")

-- Test 1: Get available colors
print("\n1. Getting available colors:")
local colors = _PY.get_available_colors()
print("Type of colors:", type(colors))
if colors then
    print("Number of colors:", #colors)
    if #colors > 0 then
        for i = 1, math.min(10, #colors) do
            print("  " .. colors[i])
        end
        if #colors > 10 then
            print("  ... and " .. (#colors - 10) .. " more")
        end
    else
        print("  Colors list is empty")
    end
else
    print("  Colors is nil")
end

-- Test 2: HTML to console conversion with font colors
print("\n2. Testing HTML to console conversion:")
local html1 = 'This is <font color="red">red text</font> and <font color="blue">blue text</font>'
local result1 = _PY.html2console(html1)
print("Original:", html1)
print("Converted:", result1)

-- Test 3: HTML with entities
print("\n3. Testing HTML entities:")
local html2 = 'Special chars: &lt;tag&gt; &amp; &quot;quotes&quot;'
local result2 = _PY.html2console(html2)
print("Original:", html2)
print("Converted:", result2)

-- Test 4: HTML with line breaks
print("\n4. Testing HTML line breaks:")
local html3 = 'Line 1<br>Line 2<br/>Line 3'
local result3 = _PY.html2console(html3)
print("Original:", html3)
print("Converted:")
print(result3)

print("\nHTML extension tests completed!")
