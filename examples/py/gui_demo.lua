-- EPLua GUI Demo Script  
-- This script demonstrates HTML window creation and web server integration

print("[Lua] Starting EPLua HTML Window Demo...")

-- Start the web server first
print("[Lua] Starting web server...")
local server_result = _PY.start_web_server("127.0.0.1", 8000)
print("[Lua] Web server result:", server_result)

-- Wait a moment for the server to start
_PY.setTimeout(function()
    -- Check if GUI is available
    local gui_available = _PY.gui_available()
    print("[Lua] GUI available:", gui_available)
    
    if gui_available then
        print("[Lua] HTML rendering available:", _PY.html_rendering_available())
        print("[Lua] HTML engine:", _PY.get_html_engine())
        print("[Lua] ")
        
        -- Create an HTML window
        print("[Lua] Creating GUI window...")
        local window_id = _PY.create_window("EPLua Demo Window", 900, 700)
        
        if string.sub(window_id, 1, 5) == "ERROR" then
            print("[Lua] Failed to create window:", window_id)
            if string.find(window_id, "main thread") then
                print("[Lua] ")
                print("[Lua] 🍎 macOS detected - Windows need main thread!")
                print("[Lua] ")
                print("[Lua] To test GUI windows, run from main thread:")
                print("[Lua] cd /Users/jangabrielsson/Documents/dev/eplua")
                print("[Lua] source .venv/bin/activate")
                print("[Lua] python test_html_window.py")
            end
        else
            print("[Lua] Window created:", window_id)
            
            -- Create some content (will be HTML if supported, text if not)
            local content = [[
<!DOCTYPE html>
<html>
<head>
    <title>EPLua Demo</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { color: #333; border-bottom: 2px solid #667eea; padding-bottom: 10px; }
        .status { background: #f0f8ff; padding: 15px; border-radius: 5px; margin: 15px 0; }
        .feature { margin: 10px 0; padding: 10px; background: #f9f9f9; border-left: 4px solid #4CAF50; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 EPLua Demo Application</h1>
        <p>GUI windows controlled from Lua scripts</p>
    </div>
    
    <div class="status">
        <h3>✅ System Status</h3>
        <p><strong>EPLua Engine:</strong> Running</p>
        <p><strong>Web Server:</strong> http://127.0.0.1:8000</p>
        <p><strong>GUI System:</strong> Active</p>
        <p><strong>Window ID:</strong> ]] .. window_id .. [[</p>
    </div>
    
    <div class="feature">
        <h4>🎯 Features Demonstrated</h4>
        <ul>
            <li>Window creation from Lua scripts</li>
            <li>Content display (HTML or text fallback)</li>
            <li>Web server integration</li>
            <li>JSON API endpoints</li>
            <li>Timer and callback system</li>
        </ul>
    </div>
    
    <div class="feature">
        <h4>🔧 API Endpoints</h4>
        <p>Test these URLs:</p>
        <ul>
            <li>GET /status - Server status</li>
            <li>POST /execute - Execute Lua code</li>
        </ul>
    </div>
    
    <div class="feature">
        <h4>💡 Notes</h4>
        <p>If you see this as formatted HTML, the HTML rendering is working!</p>
        <p>If you see this as plain text, it's using the text fallback mode.</p>
        <p>Either way, the window system is fully functional.</p>
    </div>
</body>
</html>
]]
            
            -- Set the content
            print("[Lua] Setting window content...")
            local content_result = _PY.set_window_html(window_id, content)
            print("[Lua] Content result:", content_result)
            
            -- Show the window
            print("[Lua] Showing window...")
            local show_result = _PY.show_window(window_id)
            print("[Lua] Show result:", show_result)
            
            -- Check HTML rendering capability
            local html_available = _PY.html_rendering_available()
            print("[Lua] ")
            if html_available then
                print("[Lua] ✓ HTML rendering should be available")
            else
                print("[Lua] ℹ️  Using text-only display (HTML rendering not available)")
                print("[Lua] ℹ️  This is due to tkinterweb compatibility on this system")
            end
            
            print("[Lua] ")
            print("[Lua] ✓ GUI Window Demo Complete!")
            print("[Lua] ")
            print("[Lua] The window should now be visible showing:")
            if html_available then
                print("[Lua] - Formatted HTML content with styling")
            else
                print("[Lua] - Text content (HTML source visible)")
            end
            print("[Lua] - System status information")
            print("[Lua] - Feature demonstration")
            print("[Lua] ")
        end
    else
        print("[Lua] GUI not available (tkinter not installed)")
    end
    
    print("[Lua] You can also test API endpoints:")
    print("[Lua] - GET  http://127.0.0.1:8000/status")
    print("[Lua] - POST http://127.0.0.1:8000/execute")
    print("[Lua] ")
    print("[Lua] The demo will run for 5 minutes...")
    
    -- Keep the demo running for 5 minutes
    _PY.setTimeout(function()
        print("[Lua] Demo ending...")
        -- Clean up windows
        local windows = _PY.list_windows()
        if windows ~= "No windows open" then
            print("[Lua] Cleaning up windows...")
            print("[Lua] " .. windows)
        end
    end, 300000) -- 5 minutes
    
end, 1000) -- 1 second delay

print("[Lua] HTML GUI demo script loaded. Starting components...")
