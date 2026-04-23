"""
Cross-thread dispatch for the PLua engine.

Background threads (HTTP workers, TCP/UDP/MQTT clients, FastAPI request handlers)
need to deliver three kinds of work into the main asyncio loop where the Lua
runtime lives:

1. **Callback results** — the result of a previously-registered Lua callback
   (timer, network reply, ...). Delivered via `post_callback_from_thread()`,
   drained by calling `_PY.timerExpired(callback_id, error, result)`.

2. **Fire-and-forget Lua calls** — a Python thread wants the main loop to
   invoke a `_PY.<name>(*args)` function with no return value. Delivered via
   `post_lua_call()`.

3. **Synchronous script execution** — a Python thread wants to run a Lua
   snippet (or JSON-encoded function call) and block until the result is
   available. Delivered via `execute_script_and_wait()` and resolved by Lua
   calling back into `handle_thread_request_result()`.

This module wraps the three queues + result map behind a single
`CrossThreadDispatch` object and exposes a `process_once(...)` step that the
engine's loop coroutine drains on each tick. Keeping the queue plumbing here
lets `engine.py` focus on lifecycle and the Lua/Lupa boundary.
"""

from __future__ import annotations

import logging
import queue
import time
import uuid
from collections.abc import Callable
from typing import Any

logger = logging.getLogger(__name__)


class CrossThreadDispatch:
    """Owns the three thread→loop queues and the pending-results map."""

    def __init__(self) -> None:
        # Callback results posted from worker threads.
        self._callback_queue: queue.Queue = queue.Queue()
        # Fire-and-forget _PY.<name>(*args) calls posted from worker threads.
        self._lua_call_queue: queue.Queue = queue.Queue()
        # Synchronous script execution requests + their resolved results.
        self._execution_queue: queue.Queue = queue.Queue()
        self._execution_results: dict[str, Any] = {}

    # ------------------------------------------------------------------
    # Producers (called from any thread)
    # ------------------------------------------------------------------
    def post_callback(self, callback_id: int, error: Any = None, result: Any = None) -> None:
        """Queue a callback result for delivery to Lua."""
        try:
            self._callback_queue.put_nowait((callback_id, error, result))
        except queue.Full:
            logger.error(f"Callback queue is full, dropping callback {callback_id}")

    def post_lua_call(self, func_name: str, args: tuple) -> None:
        """Queue a fire-and-forget _PY.<name>(*args) call."""
        try:
            self._lua_call_queue.put_nowait((func_name, args))
        except queue.Full:
            logger.error(f"Lua call queue is full, dropping call to {func_name}")

    def execute_script_and_wait(
        self,
        script: str,
        timeout_seconds: float = 30.0,
        is_json: bool = False,
    ) -> dict[str, Any]:
        """Submit a script for execution on the main loop and block until result."""
        request_id = str(uuid.uuid4())
        try:
            self._execution_queue.put_nowait((request_id, script, timeout_seconds, is_json))
        except queue.Full:
            return {
                "success": False,
                "result": None,
                "execution_time": 0,
                "error": "Execution queue is full",
            }

        start = time.time()
        while time.time() - start < timeout_seconds:
            if request_id in self._execution_results:
                return self._execution_results.pop(request_id)
            time.sleep(0.01)

        self._execution_results.pop(request_id, None)
        return {
            "success": False,
            "result": None,
            "execution_time": timeout_seconds,
            "error": f"Script execution timeout after {timeout_seconds} seconds",
        }

    # ------------------------------------------------------------------
    # Consumer side (called from the main loop)
    # ------------------------------------------------------------------
    def store_execution_result(self, request_id: str, result: Any) -> None:
        """Resolve a pending execute_script_and_wait() request."""
        self._execution_results[request_id] = result

    def process_once(
        self,
        lua: Any,
        py_table_convert: Callable[[Any], Any],
    ) -> None:
        """
        Drain one entry from each of the three queues, if available.

        `lua` is the Lupa runtime; `py_table_convert` is `python_to_lua_table`.
        Errors in any single queue are logged but do not stop the others.
        """
        # 1. Callback results → _PY.timerExpired(cb, err, res)
        try:
            callback_id, error, result = self._callback_queue.get_nowait()
            if error is not None and isinstance(error, (dict, list)):
                error = py_table_convert(error)
            if result is not None and isinstance(result, (dict, list)):
                result = py_table_convert(result)
            # Hold strong refs across the Lua call to keep Python 3.12's GC from
            # collecting Lupa wrapper objects mid-call.
            _keep_alive = (error, result)
            lua.globals()["_PY"]["timerExpired"](callback_id, error, result)
            del _keep_alive
        except queue.Empty:
            pass

        # 2. Fire-and-forget _PY calls
        try:
            func_name, args = self._lua_call_queue.get_nowait()
            py_func = lua.globals()["_PY"][func_name]
            if py_func is not None:
                py_func(*args)
        except queue.Empty:
            pass

        # 3. Synchronous script execution requests
        try:
            request_id, script, _timeout_seconds, is_json = self._execution_queue.get_nowait()
            start_time = time.time()
            try:
                lua.globals()["_PY"]["threadRequest"](request_id, script, is_json)
                # The result is delivered later via store_execution_result()
                # when Lua calls _PY.threadRequestResult(id, result).
            except Exception as e:
                self._execution_results[request_id] = {
                    "success": False,
                    "result": None,
                    "execution_time": time.time() - start_time,
                    "error": f"Failed to execute threadRequest: {e}",
                }
        except queue.Empty:
            pass
