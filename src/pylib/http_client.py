"""
HTTP functionality for EPLua.

This module provides HTTP request capabilities that can be called from Lua scripts.
For other network protocols, see separate modules: tcp.py, udp.py, websocket.py, mqtt.py
"""

import logging
import asyncio
import json
import requests  # For synchronous requests
from typing import Any, Dict
import aiohttp
from plua.lua_bindings import export_to_lua, get_global_engine, python_to_lua_table, lua_to_python_table

logger = logging.getLogger(__name__)


@export_to_lua("call_http")
def call_http(url: str, options: Any, callback_id: int) -> None:
    """
    Make an HTTP request with the given URL and options.
    
    Args:
        url: The URL to request
        options: Lua table with request options (method, headers, data, etc.)
        callback_id: ID of the registered Lua callback
    """
    # Convert Lua table to Python dict
    py_options = lua_to_python_table(options) if hasattr(options, 'items') else {}
    
    method = py_options.get('method', 'GET').upper()
    headers = py_options.get('headers', {})
    data = py_options.get('data')
    
    # Create options dict for the async function
    request_options = {
        'method': method,
        'headers': headers
    }
    
    if data is not None:
        request_options['data'] = data
    
    # Schedule the async request
    engine = get_global_engine()
    if engine and engine._timer_manager:
        asyncio.create_task(_perform_http_request(url, request_options, callback_id))


async def _perform_http_request(url: str, options: Dict[str, Any], callback_id: int) -> None:
    """
    Perform the actual HTTP request asynchronously.
    
    Args:
        url: The URL to request
        options: Request options (method, headers, data, etc.)
        callback_id: ID for the callback when request completes
    """
    engine = get_global_engine()
    if not engine:
        logger.error("No global engine available for HTTP callback")
        return
    
    try:
        # Extract options
        method = options.get('method', 'GET').upper()
        headers = options.get('headers', {})
        data = options.get('data')
        json_data = options.get('json')
        timeout = options.get('timeout', 30)
        
        # Prepare request kwargs
        request_kwargs = {
            'headers': headers,
            'timeout': aiohttp.ClientTimeout(total=timeout)
        }
        
        # Handle request body
        if json_data:
            request_kwargs['json'] = json_data
        elif data:
            request_kwargs['data'] = data
        
        # Make the HTTP request
        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, **request_kwargs) as response:
                # Get response text
                response_text = await response.text()
                
                # Try to parse as JSON
                try:
                    response_json = json.loads(response_text)
                except json.JSONDecodeError:
                    response_json = None
                
                # Prepare result
                result = {
                    'status': response.status,
                    'status_text': response.reason or '',
                    'headers': dict(response.headers),
                    'text': response_text,
                    'json': response_json,
                    'url': str(response.url),
                    'ok': 200 <= response.status < 300
                }
                
                logger.debug(f"HTTP request completed: {response.status} for {url}")
                
                # Call back to Lua with the result
                try:
                    # Convert response to Lua table
                    lua_result = python_to_lua_table(result)
                    engine._lua.globals()["_PY"]["timerExpired"](callback_id, None, lua_result)
                except Exception as e:
                    logger.error(f"Error calling HTTP callback {callback_id}: {e}")
                    
    except asyncio.TimeoutError:
        logger.error(f"HTTP request timeout for {url}")
        error_message = f'Request to {url} timed out after {timeout} seconds'
        try:
            engine._lua.globals()["_PY"]["timerExpired"](callback_id, error_message, None)
        except Exception as e:
            logger.error(f"Error calling HTTP timeout callback {callback_id}: {e}")
            
    except Exception as e:
        logger.error(f"HTTP request error for {url}: {e}")
        try:
            engine._lua.globals()["_PY"]["timerExpired"](callback_id, str(e), None)
        except Exception as e:
            logger.error(f"Error calling HTTP error callback {callback_id}: {e}")


@export_to_lua("http_request_sync")
def http_request_sync(options: Any) -> Any:
    """
    Make a synchronous HTTP request.
    
    Args:
        options: Lua table with request options (url, method, headers, data, etc.)
        
    Returns:
        Response table with status, body, headers, etc.
    """
    try:
        # Convert Lua table to Python dict
        py_options = lua_to_python_table(options) if hasattr(options, 'items') else {}
        
        url = py_options.get('url')
        if not url:
            return python_to_lua_table({'error': 'URL is required'})
            
        method = py_options.get('method', 'GET').upper()
        headers = py_options.get('headers', {})
        data = py_options.get('data')
        timeout = py_options.get('timeout', 30)
        
        # Make the synchronous request
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            data=data,
            timeout=timeout
        )
        
        # Try to parse JSON response
        response_json = None
        try:
            response_json = response.json()
        except Exception:
            pass
        
        # Create result
        result = {
            'status': response.status_code,
            'status_text': response.reason or '',
            'headers': dict(response.headers),
            'text': response.text,
            'json': response_json,
            'url': response.url,
            'ok': 200 <= response.status_code < 300
        }
        
        logger.debug(f"Sync HTTP request completed: {response.status_code} for {url}")
        return python_to_lua_table(result)
        
    except requests.RequestException as e:
        logger.error(f"Sync HTTP request error: {e}")
        return python_to_lua_table({'error': str(e)})
    except Exception as e:
        logger.error(f"Sync HTTP request unexpected error: {e}")
        return python_to_lua_table({'error': str(e)})
