"""
Tests for the AsyncTimerManager class.
"""

import asyncio
import pytest
from plua.timers import AsyncTimerManager


class TestAsyncTimerManager:
    """Test cases for AsyncTimerManager."""
    
    @pytest.mark.asyncio
    async def test_timer_manager_lifecycle(self):
        """Test timer manager start and stop."""
        manager = AsyncTimerManager()
        
        await manager.start()
        await manager.stop()
        
    @pytest.mark.asyncio
    async def test_set_timeout(self):
        """Test setTimeout functionality."""
        manager = AsyncTimerManager()
        await manager.start()
        
        fired = []
        
        def callback():
            fired.append(True)
            
        timer_id = manager.set_timeout(50, callback)
        assert timer_id is not None
        assert isinstance(timer_id, str)
        
        # Timer shouldn't have fired yet
        assert len(fired) == 0
        
        # Wait for timer to fire
        await asyncio.sleep(0.1)
        assert len(fired) == 1
        
        # Timer should be removed after firing
        assert manager.get_timer_count() == 0
        
        await manager.stop()
        
    @pytest.mark.asyncio
    async def test_clear_timer(self):
        """Test clearing specific timers."""
        manager = AsyncTimerManager()
        await manager.start()
        
        fired = []
        
        def callback():
            fired.append(True)
            
        timer_id = manager.set_timeout(1000, callback)  # Long timeout
        
        # Clear before it fires
        cleared = manager.clear_timer(timer_id)
        assert cleared is True
        
        # Wait to ensure it doesn't fire
        await asyncio.sleep(0.1)
        assert len(fired) == 0
        
        # Clearing non-existent timer should return False
        cleared = manager.clear_timer("non-existent")
        assert cleared is False
        
        await manager.stop()
        """Test clearing specific timers."""
        manager = AsyncTimerManager()
        await manager.start()
        
        fired = []
        
        def callback():
            fired.append(True)
            
        timer_id = manager.set_timeout(1000, callback)  # Long timeout
        
        # Clear before it fires
        cleared = manager.clear_timer(timer_id)
        assert cleared is True
        
        # Wait to ensure it doesn't fire
        await asyncio.sleep(0.1)
        assert len(fired) == 0
        
        # Clearing non-existent timer should return False
        cleared = manager.clear_timer("non-existent")
        assert cleared is False
        
        await manager.stop()
        
    @pytest.mark.asyncio
    async def test_multiple_timers(self):
        """Test handling multiple timers."""
        manager = AsyncTimerManager()
        await manager.start()
        
        fired = {}
        
        def make_callback(timer_name):
            def callback():
                fired[timer_name] = fired.get(timer_name, 0) + 1
            return callback
            
        # Create multiple timers (only setTimeout since setInterval is in Lua)
        timer1 = manager.set_timeout(30, make_callback("timer1"))
        timer2 = manager.set_timeout(60, make_callback("timer2"))
        timer3 = manager.set_timeout(90, make_callback("timer3"))
        
        assert manager.get_timer_count() == 3
        
        # Wait for timers to fire
        await asyncio.sleep(0.12)
        
        # Check results
        assert fired.get("timer1", 0) == 1  # 30ms timeout fired
        assert fired.get("timer2", 0) == 1  # 60ms timeout fired  
        assert fired.get("timer3", 0) == 1  # 90ms timeout fired
        
        # All timers should be cleaned up after firing
        assert manager.get_timer_count() == 0
        
        await manager.stop()
        
    @pytest.mark.asyncio
    async def test_timer_info(self):
        """Test getting timer information."""
        manager = AsyncTimerManager()
        await manager.start()
        
        def callback():
            pass
            
        timer_id = manager.set_timeout(1000, callback)
        
        # Get timer info
        info = manager.get_timer_info(timer_id)
        assert info is not None
        assert info["timer_id"] == timer_id
        assert info["delay"] == 1.0  # 1000ms = 1s
        assert info["running"] is True
        assert "created_at" in info
        
        # Non-existent timer should return None
        info = manager.get_timer_info("non-existent")
        assert info is None
        
        await manager.stop()
        
    @pytest.mark.asyncio
    async def test_async_callback(self):
        """Test async callback functions."""
        manager = AsyncTimerManager()
        await manager.start()
        
        fired = []
        
        async def async_callback():
            await asyncio.sleep(0.01)  # Simulate async work
            fired.append(True)
            
        timer_id = manager.set_timeout(50, async_callback)
        
        # Wait for timer to fire and callback to complete
        await asyncio.sleep(0.1)
        
        assert len(fired) == 1
        assert manager.get_timer_count() == 0
        
        await manager.stop()
        
    @pytest.mark.asyncio
    async def test_callback_error_handling(self):
        """Test error handling in callbacks."""
        manager = AsyncTimerManager()
        await manager.start()
        
        def error_callback():
            raise ValueError("Test error")
            
        timer_id = manager.set_timeout(50, error_callback)
        
        # Error in callback shouldn't crash the timer system
        await asyncio.sleep(0.1)
        
        # Timer should be cleaned up even after error
        assert manager.get_timer_count() == 0
        
        await manager.stop()
