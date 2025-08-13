-- Network modules demonstration
-- This example shows the modular network architecture

function main()
    _PY.print("=== EPLua Network Modules Demo ===")
    
    -- HTTP functionality (implemented)
    _PY.print("HTTP module: http.py")
    _PY.print("- Available: call_http() for async HTTP requests")
    
    -- Future network modules (placeholders)
    _PY.print("\nPlanned network modules:")
    _PY.print("- TCP module: tcp.py")
    _PY.print("  Functions: tcp_connect(), tcp_send(), tcp_receive()")
    
    _PY.print("- UDP module: udp.py") 
    _PY.print("  Functions: udp_socket(), udp_send(), udp_broadcast()")
    
    _PY.print("- WebSocket module: websocket.py")
    _PY.print("  Functions: ws_connect(), ws_send(), ws_close()")
    
    _PY.print("- MQTT module: mqtt.py")
    _PY.print("  Functions: mqtt_connect(), mqtt_publish(), mqtt_subscribe()")
    
    _PY.print("\n=== Modular Network Architecture ===")
    _PY.print("Each protocol has its own dedicated module for:")
    _PY.print("- Better code organization")
    _PY.print("- Easier maintenance") 
    _PY.print("- Cleaner separation of concerns")
    _PY.print("- Smaller, focused files")
end

main()
