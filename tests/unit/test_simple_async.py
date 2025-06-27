#!/usr/bin/env python3
"""Simple test to verify event loop and timer functionality"""

import asyncio


async def test_timer():
    print("Creating timer...")
    
    # Create a simple timer
    async def timer_callback():
        print("✓ Timer executed!")
    
    # Schedule the timer
    task = asyncio.create_task(asyncio.sleep(1.0))
    task.add_done_callback(lambda t: asyncio.create_task(timer_callback()))
    
    print("Timer scheduled. Waiting...")
    
    # Wait for the timer
    await asyncio.sleep(2.0)
    
    print("Test completed!")


if __name__ == "__main__":
    asyncio.run(test_timer()) 