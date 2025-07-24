-- Demo script showing shared interpreter state between REPL and API
-- This script can be loaded and then interacted with via both REPL and API

print("Demo script loaded - shared interpreter ready!")

-- Initialize some demo variables
demo_counter = 0
demo_message = "Hello from plua!"

-- Create a demo function
function increment_counter()
    demo_counter = demo_counter + 1
    return demo_counter
end

-- Create a demo table
demo_config = {
    name = "plua Demo",
    version = "1.0",
    features = {"REPL", "API", "Timers", "Networking"}
}

-- Show available demo commands
function show_demo_commands()
    print("Demo commands available in both REPL and API:")
    print("  return demo_message")
    print("  return increment_counter()")
    print("  return demo_config.name")
    print("  demo_message = 'New message'; return demo_message")
    print("")
    print("API Examples:")
    print("  curl -X POST http://localhost:8888/plua/execute -H 'Content-Type: application/json' -d '{\"code\":\"return demo_counter\"}'")
    print("  curl -X POST http://localhost:8888/plua/execute -H 'Content-Type: application/json' -d '{\"code\":\"return increment_counter()\"}'")
    print("  curl -X POST http://localhost:8888/plua/execute -H 'Content-Type: application/json' -d '{\"code\":\"return demo_config.features[1]\"}'")
end

show_demo_commands()

print("Demo initialization complete. The API server and REPL share this interpreter state.")
print("Try the commands above in either the REPL or via the API!")
