# plua2 Interactive REPL

The plua2 REPL provides an interactive Lua environment with all plua2 features available.

## Starting the REPL

```bash
# Start the REPL (no Lua file provided)
python -m src.plua2

# Or with debug mode
python -m src.plua2 --debug
```

## REPL Features

### Basic Lua
```lua
plua2> x = 42
plua2> print("Hello, world!")
Hello, world!
plua2> x + 10
52
```

### JSON Support (built-in)
```lua
plua2> data = {name = "John", age = 30}
plua2> json_str = json.encode(data)
plua2> print(json_str)
{"age":30,"name":"John"}
plua2> parsed = json.decode(json_str)
plua2> print(parsed.name)
John
```

### Async Timers
```lua
plua2> setTimeout(function() print("Timer fired!") end, 2000)
plua2> -- Wait 2 seconds...
Timer fired!
```

### Network Operations (built-in)
```lua
plua2> client = net.HTTPClient()
plua2> client:request("https://httpbin.org/json", {
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
plua2> server = net.HTTPServer()
plua2> server:start("localhost", 8080, function(method, path, payload)
  return json.encode({message = "Hello from REPL!", path = path}), 200
end)
plua2> -- Server now running on port 8080
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
plua2> function factorial(n)
  if n <= 1 then return 1 end
  return n * factorial(n - 1)
end
plua2> factorial(5)
120
```

### Async Chain
```lua
plua2> setTimeout(function()
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
plua2> client = net.HTTPClient()
plua2> client:request("https://api.github.com/users/octocat", {
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
plua2> setTimeout(function() print("Later!") end, 5000)
plua2> state()
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
- Learning plua2 features
- Testing API calls
- Prototyping async code
- Debugging network operations
- Quick calculations and experiments
