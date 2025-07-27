# plua Web REPL HTML Rendering Test Examples

The plua web REPL now supports HTML rendering! Try these examples in the web interface:

## Basic Color Examples
```lua
print("<font color='red'>This should be red!</font>")
print("<font color='green'>This should be green!</font>")
print("<font color='blue'>This should be blue!</font>")
```

## Text Formatting
```lua
print("<b>Bold text</b>")
print("<i>Italic text</i>")
print("<u>Underlined text</u>")
```

## Mixed Formatting
```lua
print("<font color='yellow'><b>Bold Yellow Text!</b></font>")
print("<span style='background-color: blue; color: white; padding: 4px;'>Highlighted text</span>")
```

## List Example
```lua
print("<ul><li><font color='cyan'>Item 1</font></li><li><font color='magenta'>Item 2</font></li></ul>")
```

## Code Example
```lua
print("<code style='background-color: #333; color: #00ff00; padding: 2px;'>function test() return 'Hello' end</code>")
```

## Complete Test
Copy and paste this complete example:

```lua
print("<h3 style='color: #4fc3f7;'>plua HTML Test</h3>")
print("<p><font color='red'>Red</font> | <font color='green'>Green</font> | <font color='blue'>Blue</font></p>")
print("<p><b>Bold</b> | <i>Italic</i> | <u>Underlined</u></p>")
print("<span style='background-color: yellow; padding: 2px;'>Highlighted</span>")
return "HTML test completed!"
```

## How to Access

1. Start plua with API: `python -m plua --api 8877`
2. Open web browser to: `http://localhost:8877/web`
3. Paste any of the above examples into the text area
4. Click "Execute" or press Ctrl+Enter (Cmd+Enter on Mac)
5. See the HTML-rendered output!

The web REPL now uses `innerHTML` instead of `textContent`, allowing HTML tags to be properly rendered in the browser.
