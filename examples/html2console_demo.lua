print("HTML2Console Extension Demo\n============================\n")

local examples = {
  "Hello <font color='red'>World</font>!",
  "Line 1<br>Line 2<br/>Line 3",
  "Space&nbsp;here",
  "<font color='blue'>Blue <font color='red'>Red</font> Blue</font>",
  "<font color='#FF0000'>Red hex</font>",
  "<font color='rgb(0,255,0)'>Green RGB</font>",
  "Nested <font color='yellow'>Yellow <font color='blue'>Blue <font color='red'>Red</font></font></font> End"
}

for i, html in ipairs(examples) do
  print(string.format("Example %d:", i))
  __print("HTML:    ", html)
  print("Console: ", html)
  print("-----------------------------")
end

print("\nAvailable color names:")
for _, color in ipairs(_PY.get_available_colors()) do
  io.write(_PY.html2console(string.format("<font color='%s'>%s</font> ", color, color)) .. " ")
end
print("\n\nDemo complete.") 