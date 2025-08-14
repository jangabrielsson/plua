
"""
HC3 Refresh States API implementation

This file contains the reference implementation for HC3-compatible 
refresh states polling and event queue management.
"""

import json
import sys
import time
import requests
from collections import deque
from threading import Thread, Lock
from datetime import datetime


# Global state for refresh states polling
_refresh_thread = None
_refresh_running = False
_events = deque(maxlen=1000)  # MAX_EVENTS = 1000
_event_count = 0
_events_lock = Lock()


def _convert_lua_table(lua_table):
    """Convert Lua table to Python dict"""
    if isinstance(lua_table, dict):
        return lua_table
    elif hasattr(lua_table, 'items'):
        return dict(lua_table.items())
    else:
        return {}


def _python_to_lua_table(lua_runtime, data):
    """Convert Python data to Lua table format"""
    # This would be implemented based on your Lua runtime
    # For now, return the data as-is for compatibility
    return data


# This would be imported from your lua_bindings module
lua_exporter = None


@lua_exporter.export(description="Start polling refresh states", category="refresh", inject_runtime=True)
def pollRefreshStates(lua_runtime, start: int, url: str, options: dict):
    """Start polling refresh states in a background thread"""
    global _refresh_thread, _refresh_running

    # Stop existing thread if running
    if _refresh_running and _refresh_thread:
        _refresh_running = False
        _refresh_thread.join(timeout=1)

    # Convert Lua options to Python dict
    options = _convert_lua_table(options)

    def refresh_runner():
        global _refresh_running, _events, _event_count
        last, retries = start, 0
        _refresh_running = True

        while _refresh_running:
            try:
                nurl = url + str(last) + "&lang=en&rand=7784634785"
                resp = requests.get(nurl, headers=options.get('headers', {}), timeout=30)
                if resp.status_code == 200:
                    retries = 0
                    data = resp.json()
                    last = data.get('last', last)

                    if data.get('events'):
                        for event in data['events']:
                            # Use addEvent function directly with dict for efficiency
                            addEvent(lua_runtime, event)

                elif resp.status_code == 401:
                    print("HC3 credentials error", file=sys.stderr)
                    print("Exiting refreshStates loop", file=sys.stderr)
                    break

            except requests.exceptions.Timeout:
                pass
            except requests.exceptions.ConnectionError:
                retries += 1
                if retries > 5:
                    print(f"Connection error: {nurl}", file=sys.stderr)
                    print("Exiting refreshStates loop", file=sys.stderr)
                    break
            except Exception as e:
                print(f"Error: {e} {nurl}", file=sys.stderr)

            # Sleep between requests
            time.sleep(1)

        _refresh_running = False

    # Start the thread
    _refresh_thread = Thread(target=refresh_runner, daemon=True)
    _refresh_thread.start()

    return {"status": "started", "thread_id": _refresh_thread.ident}


@lua_exporter.export(description="Add event to the event queue", category="refresh", inject_runtime=True)
def addEvent(lua_runtime, event):
    """Add an event to the event queue - accepts dict only"""
    global _events, _event_count

    try:
        with _events_lock:
            _event_count += 1
            event_with_counter = {'last': _event_count, 'event': event}
            _events.append(event_with_counter)

        # Call _PY.newRefreshStatesEvent if it exists (for Lua event hooks)
        try:
            if hasattr(lua_runtime.globals(), '_PY') and hasattr(lua_runtime.globals()['_PY'], 'newRefreshStatesEvent'):
                if isinstance(event, str):
                    lua_runtime.globals()['_PY']['newRefreshStatesEvent'](event)
                else:
                    lua_runtime.globals()['_PY']['newRefreshStatesEvent'](json.dumps(event))
        except Exception:
            # Silently ignore errors in event hook - don't break the queue
            pass

        return {"status": "added", "event_count": _event_count}
    except Exception as e:
        print(f"Error adding event: {e}", file=sys.stderr)
        return {"status": "error", "error": str(e)}


@lua_exporter.export(description="Add event to the event queue from Lua", category="refresh", inject_runtime=True)
def addEventFromLua(lua_runtime, event_json: str):
    """Add an event to the event queue from Lua (JSON string input)"""
    try:
        event = json.loads(event_json)
        return addEvent(lua_runtime, event)
    except Exception as e:
        print(f"Error parsing event JSON: {e}", file=sys.stderr)
        return {"status": "error", "error": str(e)}


@lua_exporter.export(description="Get events since counter", category="refresh", inject_runtime=True)
def getEvents(lua_runtime, counter: int = 0):
    """Get events since the given counter"""
    global _events, _event_count

    with _events_lock:
        events = list(_events)  # Copy to avoid race conditions
        count = events[-1]['last'] if events else 0
        evs = [e['event'] for e in events if e['last'] > counter]

    ts = datetime.now().timestamp()
    tsm = time.time()

    res = {
        'status': 'IDLE',
        'events': evs,
        'changes': [],
        'timestamp': ts,
        'timestampMillis': tsm,
        'date': datetime.fromtimestamp(ts).strftime('%H:%M | %d.%m.%Y'),
        'last': count
    }

    # Return as Lua table directly
    return _python_to_lua_table(lua_runtime, res)


@lua_exporter.export(description="Stop refresh states polling", category="refresh", inject_runtime=True)
def stopRefreshStates(lua_runtime):
    """Stop refresh states polling"""
    try:
        if hasattr(lua_runtime, '_refresh_thread') and lua_runtime._refresh_thread:
            lua_runtime._refresh_thread.stop()
            lua_runtime._refresh_thread = None
            return True
        return False
    except Exception as e:
        print(f"Error stopping refresh states: {e}", file=sys.stderr)
        return False


@lua_exporter.export(description="Get refresh states status", category="refresh", inject_runtime=True)
def getRefreshStatesStatus(lua_runtime):
    """Get refresh states polling status"""
    try:
        if hasattr(lua_runtime, '_refresh_thread') and lua_runtime._refresh_thread:
            return {
                'running': lua_runtime._refresh_thread.is_alive(),
                'url': lua_runtime._refresh_thread.url,
                'start': lua_runtime._refresh_thread.start,
                'options': lua_runtime._refresh_thread.options
            }
        return {'running': False}
    except Exception as e:
        print(f"Error getting refresh states status: {e}", file=sys.stderr)
        return {'running': False, 'error': str(e)}