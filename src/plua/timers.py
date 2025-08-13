"""
Async Timer Manager for Lua Engine

This module provides basic async timer functionality (setTimeout only) that can be controlled from Lua scripts.
The Lua layer builds setInterval on top of setTimeout.
"""

import asyncio
import logging
import time
import uuid
from typing import Callable, Dict, Optional, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class TimerInfo:
    """Information about a timer."""
    timer_id: str
    delay: float
    callback: Callable
    task: Optional[asyncio.Task] = None
    created_at: float = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = time.time()


class AsyncTimerManager:
    """
    Manages async timers that can be created and controlled from Lua scripts.

    Provides only setTimeout functionality - setInterval is implemented in Lua
    by chaining setTimeout calls.
    """

    def __init__(self):
        self._timers: Dict[str, TimerInfo] = {}
        self._running = False

    async def start(self):
        """Start the timer manager."""
        self._running = True
        logger.info("AsyncTimerManager started")

    async def stop(self):
        """Stop the timer manager and cancel all timers."""
        self._running = False
        await self.clear_all_timers()
        logger.info("AsyncTimerManager stopped")

    def set_timeout(self, delay_ms: int, callback: Callable, *args, **kwargs) -> str:
        """
        Set a one-time timer (like JavaScript setTimeout).

        Args:
            delay_ms: Delay in milliseconds
            callback: Function to call when timer fires
            *args, **kwargs: Arguments to pass to callback

        Returns:
            Timer ID that can be used to cancel the timer
        """
        delay_seconds = delay_ms / 1000.0
        timer_id = str(uuid.uuid4())

        async def timer_task():
            try:
                await asyncio.sleep(delay_seconds)
                if timer_id in self._timers and self._running:
                    logger.debug(f"Timeout timer {timer_id} firing")
                    await self._safe_call_callback(callback, *args, **kwargs)
                    # Remove timer after it fires
                    self._timers.pop(timer_id, None)
            except asyncio.CancelledError:
                logger.debug(f"Timeout timer {timer_id} cancelled")
            except Exception as e:
                logger.error(f"Error in timeout timer {timer_id}: {e}")

        task = asyncio.create_task(timer_task())
        timer_info = TimerInfo(
            timer_id=timer_id,
            delay=delay_seconds,
            callback=callback,
            task=task
        )

        self._timers[timer_id] = timer_info
        logger.debug(f"Created timeout timer {timer_id} with delay {delay_ms}ms")
        return timer_id

    def clear_timer(self, timer_id: str) -> bool:
        """
        Clear a specific timer (like JavaScript clearTimeout).

        Args:
            timer_id: ID of the timer to clear

        Returns:
            True if timer was found and cleared, False otherwise
        """
        timer_info = self._timers.pop(timer_id, None)
        if timer_info:
            if timer_info.task:
                timer_info.task.cancel()
            logger.debug(f"Cleared timer {timer_id}")
            return True
        return False

    async def clear_all_timers(self):
        """Clear all timers."""
        timer_ids = list(self._timers.keys())
        for timer_id in timer_ids:
            self.clear_timer(timer_id)

        # Wait for all tasks to complete cancellation
        tasks = [info.task for info in self._timers.values() if info.task]
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

        self._timers.clear()
        logger.debug("Cleared all timers")

    def get_timer_count(self) -> int:
        """Get the number of active timers."""
        return len(self._timers)

    def get_timer_info(self, timer_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific timer."""
        timer_info = self._timers.get(timer_id)
        if timer_info:
            return {
                "timer_id": timer_info.timer_id,
                "delay": timer_info.delay,
                "created_at": timer_info.created_at,
                "running": timer_info.task and not timer_info.task.done()
            }
        return None

    async def _safe_call_callback(self, callback: Callable, *args, **kwargs):
        """Safely call a callback function, handling both sync and async functions."""
        try:
            if asyncio.iscoroutinefunction(callback):
                await callback(*args, **kwargs)
            else:
                callback(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in timer callback: {e}")
            # Don't re-raise to prevent timer system from crashing
