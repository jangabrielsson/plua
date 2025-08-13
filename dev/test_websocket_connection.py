#!/usr/bin/env python3
"""Test WebSocket connection to EPLua FastAPI server"""

import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://localhost:8080/ws"
    
    try:
        print(f"🔗 Connecting to {uri}...")
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connected successfully!")
            
            # Send a test message
            test_message = json.dumps({"type": "test", "message": "Hello from test client"})
            await websocket.send(test_message)
            print(f"📤 Sent: {test_message}")
            
            # Keep connection alive for a few seconds
            try:
                await asyncio.wait_for(websocket.recv(), timeout=5.0)
            except asyncio.TimeoutError:
                print("⏰ No message received (expected)")
                
    except Exception as e:
        print(f"❌ WebSocket connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket())
