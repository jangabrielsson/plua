# plua Interactive REPL

The plua REPL provides an interactive Lua environment with all plua features available.

## Starting the REPL

```bash
# Start the REPL (no Lua file provided)
python -m src.plua

# Or with debug mode
python -m src.plua --debug
```

## REPL Features

### Basic Lua
```lua
plua> x = 42
plua> print("Hello, world!")
Hello, world!
plua> x + 10
52
```

### JSON Support (built-in)
```lua
plua> data = {name = "John", age = 30}
plua> json_str = json.encode(data)
plua> print(json_str)
{"age":30,"name":"John"}
plua> parsed = json.decode(json_str)
plua> print(parsed.name)
John
```

### Async Timers
```lua
plua> setTimeout(function() print("Timer fired!") end, 2000)
plua> -- Wait 2 seconds...
Timer fired!
```

### Network Operations (built-in)
```lua
plua> client = net.HTTPClient()
plua> client:request("https://httpbin.org/json", {
  success = function(resp) 
    print("Status:", resp.status)
    local data = json.decode(resp.data)
    print("Slideshow title:", data.slideshow.title)
  end,
  error = function(err) print("Error:", err) end
})
```

### HTTP Server
```lua
plua> server = net.HTTPServer()
plua> server:start("localhost", 8080, function(method, path, payload)
  return json.encode({message = "Hello from REPL!", path = path}), 200
end)
plua> -- Server now running on port 8080
```

## REPL Commands

- `help()` - Show help information
- `state()` - Show runtime state (timers, callbacks, tasks)
- `debug(true/false)` - Toggle debug mode
- `exit()` - Exit the REPL
- Ctrl+C - Cancel current input (continue REPL)
- Ctrl+D - Exit the REPL

## Examples

### Simple Calculation
```lua
plua> function factorial(n)
  if n <= 1 then return 1 end
  return n * factorial(n - 1)
end
plua> factorial(5)
120
```

### Async Chain
```lua
plua> setTimeout(function()
  print("Step 1")
  setTimeout(function()
    print("Step 2")
    setTimeout(function()
      print("Step 3 - Done!")
    end, 1000)
  end, 1000)
end, 1000)
```

### HTTP Client Example
```lua
plua> client = net.HTTPClient()
plua> client:request("https://api.github.com/users/octocat", {
  success = function(resp)
    local user = json.decode(resp.data)
    print("GitHub user:", user.login)
    print("Public repos:", user.public_repos)
  end,
  error = function(err)
    print("Failed to fetch user:", err)
  end
})
```

## Runtime State Monitoring

Use `state()` to see what's happening:

```lua
plua> setTimeout(function() print("Later!") end, 5000)
plua> state()
Runtime state:
  Active timers: 1
  Pending callbacks: 0
  Total tasks: 1
  Asyncio tasks: 3
    - repl_main
    - callback_loop
    - lua_timer_1_5000ms
```

## Tips

1. **Multi-line input**: Currently each line is executed immediately. For complex functions, define them on a single line or use semicolons
2. **Async operations**: The REPL continues running while timers and network operations execute in the background
3. **Error recovery**: Lua errors won't crash the REPL, you can continue typing
4. **State persistence**: Variables and functions remain available throughout the REPL session
5. **Debug mode**: Use `--debug` flag or `debug(true)` for verbose logging

The REPL is perfect for:
- Learning plua features
- Testing API calls
- Prototyping async code
- Debugging network operations
- Quick calculations and experiments
