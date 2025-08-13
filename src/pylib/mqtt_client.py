"""
MQTT client functionality for EPLua
Provides async MQTT operations using aiomqtt
"""

import asyncio
import uuid
import ssl
from typing import Dict, Any, Optional
from eplua.lua_bindings import export_to_lua, get_global_engine, python_to_lua_table, lua_to_python_table
import logging

logger = logging.getLogger(__name__)

# Global storage for MQTT clients
_mqtt_clients: Dict[str, Dict[str, Any]] = {}
_mqtt_counter = 0

try:
    from aiomqtt import Client as AioMQTTClient, MqttError
    AIOMQTT_AVAILABLE = True
except ImportError:
    logger.warning("aiomqtt not available. MQTT functionality will be limited.")
    AIOMQTT_AVAILABLE = False
    AioMQTTClient = None
    MqttError = Exception

def _generate_client_id() -> str:
    """Generate unique client ID"""
    global _mqtt_counter
    _mqtt_counter += 1
    return f"eplua_mqtt_{_mqtt_counter}"

def _parse_uri(uri: str, options: Dict = None) -> Dict[str, Any]:
    """Parse MQTT URI and extract connection details"""
    # Convert Lua table to Python dict if needed
    if options is not None:
        opts = lua_to_python_table(options)
    else:
        opts = {}
    
    # Default values
    host = uri
    port = 1883
    use_tls = False
    
    # Parse URI scheme
    if uri.startswith('mqtts://'):
        use_tls = True
        host = uri[8:]  # Remove 'mqtts://'
        port = 8883
    elif uri.startswith('mqtt://'):
        host = uri[7:]  # Remove 'mqtt://'
        port = 1883
    
    # Extract host and port if specified
    if ':' in host:
        host_parts = host.split(':')
        host = host_parts[0]
        port = int(host_parts[1])
    
    # Override port if specified in options
    if 'port' in opts:
        port = opts['port']
    
    return {
        'host': host,
        'port': port,
        'use_tls': use_tls,
        'client_id': opts.get('clientId', f"eplua_mqtt_{uuid.uuid4().hex[:8]}"),
        'keep_alive': opts.get('keepAlivePeriod', 60),
        'username': opts.get('username'),
        'password': opts.get('password'),
        'clean_session': opts.get('cleanSession', True)
    }

@export_to_lua("mqtt_client_connect")
def mqtt_client_connect(uri: str, options: Optional[Dict] = None, callback_id: Optional[str] = None) -> str:
    """
    Connect to MQTT broker
    
    Args:
        uri: Broker URI (mqtt://host:port or mqtts://host:port or just host)
        options: Connection options dict
        callback_id: Optional callback for connection events
    
    Returns:
        MQTT client ID
    """
    if not AIOMQTT_AVAILABLE:
        logger.error("MQTT functionality requires aiomqtt package")
        if callback_id:
            engine = get_global_engine()
            if engine:
                engine.post_callback_from_thread(callback_id, python_to_lua_table({
                    'event': 'error',
                    'error': 'aiomqtt package not available',
                    'success': False
                }))
        return "error_no_aiomqtt"
    
    client_id = _generate_client_id()
    conn_params = _parse_uri(uri, options)
    
    # Store client info
    client_info = {
        'client': None,
        'connected': False,
        'subscriptions': set(),
        'connection_params': conn_params,
        'message_task': None,
        'main_callback_id': callback_id,
        'event_listeners': {}  # Store event-specific callbacks
    }
    _mqtt_clients[client_id] = client_info
    
    # Start the async connection task
    try:
        # Check if we're in an async context
        try:
            loop = asyncio.get_running_loop()
            task = loop.create_task(_mqtt_connect_and_listen(client_id))
            client_info['message_task'] = task
            logger.debug(f"MQTT task created successfully for client {client_id}")
        except RuntimeError:
            # No running loop, try to schedule for later
            task = asyncio.create_task(_mqtt_connect_and_listen(client_id))
            client_info['message_task'] = task
            logger.debug(f"MQTT task scheduled for client {client_id}")
            
    except Exception as e:
        logger.error(f"Failed to create MQTT task: {e}")
        # Clean up client info
        del _mqtt_clients[client_id]
        if callback_id:
            engine = get_global_engine()
            if engine:
                engine.post_callback_from_thread(callback_id, python_to_lua_table({
                    'event': 'error',
                    'error': f'Failed to create task: {e}',
                    'success': False
                }))
        return "error_task_creation"
    
    return client_id

async def _mqtt_connect_and_listen(client_id: str):
    """Connect to MQTT broker and listen for messages"""
    if client_id not in _mqtt_clients:
        return
        
    client_info = _mqtt_clients[client_id]
    conn_params = client_info['connection_params']
    callback_id = client_info['main_callback_id']
    
    try:
        # Create TLS context if needed
        tls_context = None
        if conn_params['use_tls']:
            tls_context = ssl.create_default_context()
        
        # Connect to MQTT broker
        async with AioMQTTClient(
            hostname=conn_params['host'],
            port=conn_params['port'],
            username=conn_params['username'],
            password=conn_params['password'],
            identifier=conn_params['client_id'],
            keepalive=conn_params['keep_alive'],
            clean_session=conn_params['clean_session'],
            tls_context=tls_context
        ) as client:
            client_info['client'] = client
            client_info['connected'] = True
            
            # Notify connection success
            if callback_id:
                engine = get_global_engine()
                if engine:
                    engine.post_callback_from_thread(callback_id, python_to_lua_table({
                        'event': 'connected',
                        'client_id': client_id,
                        'success': True
                    }))
            
            # Also call 'connected' event listeners
            if 'connected' in client_info['event_listeners']:
                event_callback_id = client_info['event_listeners']['connected']
                engine = get_global_engine()
                if engine:
                    engine.post_callback_from_thread(event_callback_id, python_to_lua_table({
                        'event': 'connected',
                        'client_id': client_id
                    }))
            
            # Listen for messages
            async for message in client.messages:
                # Send to main callback if exists
                if callback_id:
                    engine = get_global_engine()
                    if engine:
                        engine.post_callback_from_thread(callback_id, python_to_lua_table({
                            'event': 'message',
                            'client_id': client_id,
                            'topic': str(message.topic),
                            'payload': message.payload.decode('utf-8', errors='replace'),
                            'qos': message.qos,
                            'retain': message.retain
                        }))
                
                # Also send to 'message' event listeners
                if 'message' in client_info['event_listeners']:
                    event_callback_id = client_info['event_listeners']['message']
                    engine = get_global_engine()
                    if engine:
                        engine.post_callback_from_thread(event_callback_id, python_to_lua_table({
                            'event': 'message',
                            'client_id': client_id,
                            'topic': str(message.topic),
                            'payload': message.payload.decode('utf-8', errors='replace'),
                            'qos': message.qos,
                            'retain': message.retain
                        }))
                        
    except Exception as e:
        logger.error(f"MQTT connection error: {e}")
        client_info['connected'] = False
        
        # Notify main callback
        if callback_id:
            engine = get_global_engine()
            if engine:
                engine.post_callback_from_thread(callback_id, python_to_lua_table({
                    'event': 'error',
                    'client_id': client_id,
                    'error': str(e),
                    'success': False
                }))
        
        # Notify error event listeners
        if 'error' in client_info['event_listeners']:
            event_callback_id = client_info['event_listeners']['error']
            engine = get_global_engine()
            if engine:
                engine.post_callback_from_thread(event_callback_id, python_to_lua_table({
                    'event': 'error',
                    'client_id': client_id,
                    'error': str(e)
                }))
    finally:
        # Clean up client info
        client_info['connected'] = False
        
        # Notify disconnection
        if callback_id:
            engine = get_global_engine()
            if engine:
                engine.post_callback_from_thread(callback_id, python_to_lua_table({
                    'event': 'disconnected',
                    'client_id': client_id
                }))
        
        # Notify disconnected event listeners
        if 'disconnected' in client_info['event_listeners']:
            event_callback_id = client_info['event_listeners']['disconnected']
            engine = get_global_engine()
            if engine:
                engine.post_callback_from_thread(event_callback_id, python_to_lua_table({
                    'event': 'disconnected',
                    'client_id': client_id
                }))

@export_to_lua("mqtt_client_disconnect")
def mqtt_client_disconnect(client_id: str, callback_id: Optional[str] = None) -> None:
    """
    Disconnect MQTT client
    
    Args:
        client_id: MQTT client ID
        callback_id: Optional callback for disconnect result
    """
    if client_id not in _mqtt_clients:
        if callback_id:
            engine = get_global_engine()
            if engine:
                engine.post_callback_from_thread(callback_id, python_to_lua_table({
                    'success': False,
                    'error': 'Client not found'
                }))
        return
    
    client_info = _mqtt_clients[client_id]
    
    # Cancel message listening task
    if client_info['message_task']:
        client_info['message_task'].cancel()
    
    # Mark as disconnected
    client_info['connected'] = False
    
    # Clean up
    del _mqtt_clients[client_id]
    
    if callback_id:
        engine = get_global_engine()
        if engine:
            engine.post_callback_from_thread(callback_id, python_to_lua_table({
                'success': True
            }))

@export_to_lua("mqtt_client_publish")
def mqtt_client_publish(client_id: str, topic: str, payload: str, options: Optional[Dict] = None, callback_id: Optional[str] = None) -> None:
    """
    Publish MQTT message
    
    Args:
        client_id: MQTT client ID
        topic: Topic to publish to
        payload: Message payload
        options: Publish options (qos, retain)
        callback_id: Optional callback for publish result
    """
    if client_id not in _mqtt_clients:
        if callback_id:
            engine = get_global_engine()
            if engine:
                engine.post_callback_from_thread(callback_id, python_to_lua_table({
                    'success': False,
                    'error': 'Client not found'
                }))
        return
    
    client_info = _mqtt_clients[client_id]
    
    if not client_info['connected']:
        if callback_id:
            engine = get_global_engine()
            if engine:
                engine.post_callback_from_thread(callback_id, python_to_lua_table({
                    'success': False,
                    'error': 'Client not connected'
                }))
        return
    
    # Convert Lua table to Python dict if needed
    if options is not None:
        opts = lua_to_python_table(options)
    else:
        opts = {}
    qos = opts.get('qos', 0)
    retain = opts.get('retain', False)
    
    # Schedule the async publish task
    try:
        asyncio.create_task(_mqtt_publish(client_id, topic, payload, qos, retain, callback_id))
    except RuntimeError as e:
        if callback_id:
            engine = get_global_engine()
            if engine:
                engine.post_callback_from_thread(callback_id, python_to_lua_table({
                    'success': False,
                    'error': f'Failed to create task: {e}'
                }))

async def _mqtt_publish(client_id: str, topic: str, payload: str, qos: int, retain: bool, callback_id: Optional[str]):
    """Async MQTT publish"""
    if client_id not in _mqtt_clients:
        return
    
    client_info = _mqtt_clients[client_id]
    client = client_info['client']
    
    try:
        await client.publish(topic, payload, qos=qos, retain=retain)
        
        if callback_id:
            engine = get_global_engine()
            if engine:
                engine.post_callback_from_thread(callback_id, python_to_lua_table({
                    'success': True,
                    'topic': topic
                }))
                
    except Exception as e:
        logger.error(f"MQTT publish error: {e}")
        if callback_id:
            engine = get_global_engine()
            if engine:
                engine.post_callback_from_thread(callback_id, python_to_lua_table({
                    'success': False,
                    'error': str(e)
                }))

@export_to_lua("mqtt_client_subscribe")
def mqtt_client_subscribe(client_id: str, topic: str, options: Optional[Dict] = None, callback_id: Optional[str] = None) -> None:
    """
    Subscribe to MQTT topic
    
    Args:
        client_id: MQTT client ID
        topic: Topic to subscribe to
        options: Subscribe options (qos)
        callback_id: Optional callback for subscribe result
    """
    if client_id not in _mqtt_clients:
        if callback_id:
            engine = get_global_engine()
            if engine:
                engine.post_callback_from_thread(callback_id, python_to_lua_table({
                    'success': False,
                    'error': 'Client not found'
                }))
        return
    
    client_info = _mqtt_clients[client_id]
    
    if not client_info['connected']:
        if callback_id:
            engine = get_global_engine()
            if engine:
                engine.post_callback_from_thread(callback_id, python_to_lua_table({
                    'success': False,
                    'error': 'Client not connected'
                }))
        return
    
    # Convert Lua table to Python dict if needed
    if options is not None:
        opts = lua_to_python_table(options)
    else:
        opts = {}
    qos = opts.get('qos', 0)
    
    # Schedule the async subscribe task
    try:
        asyncio.create_task(_mqtt_subscribe(client_id, topic, qos, callback_id))
    except RuntimeError as e:
        if callback_id:
            engine = get_global_engine()
            if engine:
                engine.post_callback_from_thread(callback_id, python_to_lua_table({
                    'success': False,
                    'error': f'Failed to create task: {e}'
                }))

async def _mqtt_subscribe(client_id: str, topic: str, qos: int, callback_id: Optional[str]):
    """Async MQTT subscribe"""
    if client_id not in _mqtt_clients:
        return
    
    client_info = _mqtt_clients[client_id]
    client = client_info['client']
    
    try:
        await client.subscribe(topic, qos=qos)
        client_info['subscriptions'].add(topic)
        
        if callback_id:
            engine = get_global_engine()
            if engine:
                engine.post_callback_from_thread(callback_id, python_to_lua_table({
                    'success': True,
                    'topic': topic
                }))
                
    except Exception as e:
        logger.error(f"MQTT subscribe error: {e}")
        if callback_id:
            engine = get_global_engine()
            if engine:
                engine.post_callback_from_thread(callback_id, python_to_lua_table({
                    'success': False,
                    'error': str(e)
                }))

@export_to_lua("mqtt_client_unsubscribe")
def mqtt_client_unsubscribe(client_id: str, topic: str, callback_id: Optional[str] = None) -> None:
    """
    Unsubscribe from MQTT topic
    
    Args:
        client_id: MQTT client ID
        topic: Topic to unsubscribe from
        callback_id: Optional callback for unsubscribe result
    """
    if client_id not in _mqtt_clients:
        if callback_id:
            engine = get_global_engine()
            if engine:
                engine.post_callback_from_thread(callback_id, python_to_lua_table({
                    'success': False,
                    'error': 'Client not found'
                }))
        return
    
    client_info = _mqtt_clients[client_id]
    
    if not client_info['connected']:
        if callback_id:
            engine = get_global_engine()
            if engine:
                engine.post_callback_from_thread(callback_id, python_to_lua_table({
                    'success': False,
                    'error': 'Client not connected'
                }))
        return
    
    # Schedule the async unsubscribe task
    try:
        asyncio.create_task(_mqtt_unsubscribe(client_id, topic, callback_id))
    except RuntimeError as e:
        if callback_id:
            engine = get_global_engine()
            if engine:
                engine.post_callback_from_thread(callback_id, python_to_lua_table({
                    'success': False,
                    'error': f'Failed to create task: {e}'
                }))

async def _mqtt_unsubscribe(client_id: str, topic: str, callback_id: Optional[str]):
    """Async MQTT unsubscribe"""
    if client_id not in _mqtt_clients:
        return
    
    client_info = _mqtt_clients[client_id]
    client = client_info['client']
    
    try:
        await client.unsubscribe(topic)
        client_info['subscriptions'].discard(topic)
        
        if callback_id:
            engine = get_global_engine()
            if engine:
                engine.post_callback_from_thread(callback_id, python_to_lua_table({
                    'success': True,
                    'topic': topic
                }))
                
    except Exception as e:
        logger.error(f"MQTT unsubscribe error: {e}")
        if callback_id:
            engine = get_global_engine()
            if engine:
                engine.post_callback_from_thread(callback_id, python_to_lua_table({
                    'success': False,
                    'error': str(e)
                }))

@export_to_lua("mqtt_client_is_connected")
def mqtt_client_is_connected(client_id: str) -> bool:
    """
    Check if MQTT client is connected
    
    Args:
        client_id: MQTT client ID
    
    Returns:
        True if connected, False otherwise
    """
    if client_id not in _mqtt_clients:
        return False
    
    return _mqtt_clients[client_id]['connected']

@export_to_lua("mqtt_client_get_info")
def mqtt_client_get_info(client_id: str) -> Optional[Dict]:
    """
    Get MQTT client information
    
    Args:
        client_id: MQTT client ID
    
    Returns:
        Client info dict or None
    """
    if client_id not in _mqtt_clients:
        return None
    
    client_info = _mqtt_clients[client_id]
    conn_params = client_info['connection_params']
    
    return python_to_lua_table({
        'connected': client_info['connected'],
        'client_id': conn_params['client_id'],
        'host': conn_params['host'],
        'port': conn_params['port'],
        'use_tls': conn_params['use_tls'],
        'subscriptions': list(client_info['subscriptions'])
    })

@export_to_lua("mqtt_client_add_event_listener")
def mqtt_client_add_event_listener(client_id: str, event_name: str, callback_id: str) -> None:
    """
    Add event listener to MQTT client
    
    Args:
        client_id: MQTT client ID
        event_name: Event name (connected, disconnected, message, error)
        callback_id: Callback function ID
    """
    if client_id not in _mqtt_clients:
        return
    
    client_info = _mqtt_clients[client_id]
    client_info['event_listeners'][event_name] = callback_id

@export_to_lua("mqtt_client_remove_event_listener")
def mqtt_client_remove_event_listener(client_id: str, event_name: str) -> None:
    """
    Remove event listener from MQTT client
    
    Args:
        client_id: MQTT client ID
        event_name: Event name
    """
    if client_id not in _mqtt_clients:
        return
    
    client_info = _mqtt_clients[client_id]
    if event_name in client_info['event_listeners']:
        del client_info['event_listeners'][event_name]
