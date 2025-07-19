-- Test script for HTML rendering in plua2 web REPL
-- This demonstrates various HTML tags that should render properly

print("<h2 style='color: #4fc3f7;'>plua2 HTML Rendering Test</h2>")

print("<p><font color='red'>Red text</font> | <font color='green'>Green text</font> | <font color='blue'>Blue text</font></p>")

print("<p><b>Bold text</b> | <i>Italic text</i> | <u>Underlined text</u></p>")

print("<p><span style='background-color: yellow; padding: 2px;'>Highlighted text</span></p>")

print("<ul>")
print("  <li><font color='cyan'>List item 1</font></li>")
print("  <li><font color='magenta'>List item 2</font></li>")
print("  <li><font color='orange'>List item 3</font></li>")
print("</ul>")

print("<p><code style='background-color: #333; color: #fff; padding: 2px;'>Code formatting</code></p>")

print("<p><small>Small text</small> | Normal text | <big>Big text</big></p>")

return "HTML rendering test completed!"
