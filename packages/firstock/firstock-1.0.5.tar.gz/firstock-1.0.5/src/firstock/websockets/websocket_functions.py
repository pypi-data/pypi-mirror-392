import json
import logging
import time
from typing import Dict, List, Optional, Callable
from urllib.parse import urlencode
from enum import Enum
import websocket
import threading

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UpdateType(Enum):
    ORDER = "order"
    POSITION = "position"
    MARKET_FEED = "market_feed"
    OPTION_GREEKS = "option_greeks"


class SafeConn:
    def __init__(self, ws):
        self.ws = ws
        self.lock = threading.Lock()


class ConnectionManager:
    def __init__(self):
        self.conn_map: Dict[SafeConn, bool] = {}
        self.index_map: Dict[websocket.WebSocket, SafeConn] = {}
        self.lock = threading.Lock()

    def count_connections(self) -> int:
        with self.lock:
            return len(self.conn_map)
    
    def add_connection(self, ws: websocket.WebSocket) -> SafeConn:
        with self.lock:
            if ws in self.index_map:
                logger.info("Connection already exists")
                return self.index_map[ws]
            
            safe = SafeConn(ws)
            self.conn_map[safe] = True
            self.index_map[ws] = safe
            logger.info("Connection added")
            return safe
    
    def check_if_connection_exists(self, ws: websocket.WebSocket) -> bool:
        with self.lock:
            return ws in self.index_map
    
    def write_message(self, ws: websocket.WebSocket, data: bytes) -> Optional[str]:#write to a specific connection
        with self.lock:
            safe = self.index_map.get(ws)
        
        if not safe:
            return "connection not found"
        
        with safe.lock:
            try:
                safe.ws.send(data)
                return None
            except Exception as e:
                return str(e)

    def delete_connection(self, ws: websocket.WebSocket):
        with self.lock:
            if ws in self.index_map:
                # Set shutdown flag BEFORE closing
                _set_shutdown_flag(ws)

                safe = self.index_map[ws]
                del self.conn_map[safe]
                del self.index_map[ws]
                try:
                    safe.ws.close()
                except:
                    pass
                logger.info("Connection deleted")

                # Clear subscription tracking
                _clear_tracked_subscriptions(ws)
                return
            logger.info("Connection not found")


connections = ConnectionManager()

subscription_tracker = {}

def _track_subscription(ws: websocket.WebSocket, tokens: List[str], subscription_type: str):
    """Track subscriptions for reconnection purposes"""
    ws_id = id(ws)
    if ws_id not in subscription_tracker:
        subscription_tracker[ws_id] = {
            'tokens': [],
            'option_greeks_tokens': []
        }
    
    for token in tokens:
        if token not in subscription_tracker[ws_id][subscription_type]:
            subscription_tracker[ws_id][subscription_type].append(token)
    
    logger.debug(f"Tracked subscription: {subscription_type} - {tokens}")

def _untrack_subscription(ws: websocket.WebSocket, tokens: List[str], subscription_type: str):
    """Remove tokens from tracking when unsubscribed"""
    ws_id = id(ws)
    if ws_id in subscription_tracker and subscription_type in subscription_tracker[ws_id]:
        for token in tokens:
            if token in subscription_tracker[ws_id][subscription_type]:
                subscription_tracker[ws_id][subscription_type].remove(token)
    
    logger.debug(f"Untracked subscription: {subscription_type} - {tokens}")

def _get_tracked_subscriptions(ws: websocket.WebSocket) -> dict:
    """Get all tracked subscriptions for a connection"""
    ws_id = id(ws)
    return subscription_tracker.get(ws_id, {'tokens': [], 'option_greeks_tokens': []})

def _clear_tracked_subscriptions(ws: websocket.WebSocket):
    """Clear subscription tracking when connection is closed"""
    ws_id = id(ws)
    if ws_id in subscription_tracker:
        del subscription_tracker[ws_id]
        logger.debug(f"Cleared subscription tracking for connection {ws_id}")

def get_url_and_header_data(user_id: str, config: dict) -> tuple:
    
    scheme = config.get('scheme', 'wss')
    host = config.get('host')
    path = config.get('path')
    src_val = config.get('source', 'API')
    accept_encoding = config.get('accept_encoding', 'gzip, deflate, br')
    accept_language = config.get('accept_language', 'en-US,en;q=0.9')
    origin = config.get('origin', '')
    
    base_url = f"{scheme}://{host}{path}"
    logger.info(f"Connecting to {base_url}")

    
    with open('config.json', 'r') as f:
        config_json = json.load(f)

    user_id = list(config_json.keys())[0]
    jkey = config_json[user_id]['jKey']
    
    query_params = {
        'userId': user_id, 
        'jKey': jkey ,   
        'source': "developer-api"  
    }
    
    url_with_params = f"{base_url}?{urlencode(query_params)}"
    
    headers = {
        'accept-encoding': accept_encoding,
        'accept-language': accept_language,
        'cache-control': 'no-cache',
        'origin': origin,
        'pragma': 'no-cache'
    }
    
    return url_with_params, headers, None


def _identify_update_type(data: Dict) -> UpdateType:
    if "norenordno" in data:
        return UpdateType.ORDER
    elif "brkname" in data:
        return UpdateType.POSITION
    elif "gamma" in data: 
        return UpdateType.OPTION_GREEKS
    else:
        return UpdateType.MARKET_FEED

def _handle_authentication_response(message: str) -> bool:
    if "Authentication successful" in message:
        logger.info("Authentication successful")
        return True
    elif '"status":"failed"' in message:
        logger.warning(f"Authentication failed: {message}")
        return False
    return True



shutdown_flags = {}  # Track intentional shutdowns

def _set_shutdown_flag(ws: websocket.WebSocket):
    """Mark connection for graceful shutdown (no reconnection)"""
    ws_id = id(ws)
    shutdown_flags[ws_id] = True
    logger.debug(f"Shutdown flag set for connection {ws_id}")

def _is_shutdown_requested(ws: websocket.WebSocket) -> bool:
    """Check if shutdown was requested for this connection"""
    ws_id = id(ws)
    return shutdown_flags.get(ws_id, False)

def _clear_shutdown_flag(ws: websocket.WebSocket):
    """Clear shutdown flag"""
    ws_id = id(ws)
    if ws_id in shutdown_flags:
        del shutdown_flags[ws_id]
        logger.debug(f"Shutdown flag cleared for connection {ws_id}")

def read_message(user_id: str, ws: websocket.WebSocket, model: dict, config: dict):
    max_retries = config.get('max_websocket_connection_retries', 3)
    time_interval = config.get('time_interval', 5)
    
    message_count = 0
    is_authenticated = True
    
    # Initial subscriptions (for reference, but we'll use tracker)
    subscribed_tokens = model.get('tokens', [])
    subscribed_option_greeks_tokens = model.get('option_greeks_tokens', [])
    
    logger.info(f"Starting message reader for user {user_id}")
    logger.info(f"Callbacks configured - Feed: {model.get('subscribe_feed_data') is not None}, "
                f"Order: {model.get('order_data') is not None}, "
                f"Position: {model.get('position_data') is not None}, "
                f"Option Greeks: {model.get('subscribe_option_greeks_data') is not None}")
    
    while True:
        if not connections.check_if_connection_exists(ws):
            logger.info("Connection no longer exists, stopping reader")
            _clear_shutdown_flag(ws)
            return
        
        try:
            message = ws.recv()
            message_count += 1
            
            logger.debug(f"Message #{message_count}: {message[:200]}...")
            
            if not message:
                logger.debug("Empty message received, skipping")
                continue
            
            try:
                data = json.loads(message)
            except json.JSONDecodeError as e:
                logger.error(f"JSON parse error: {e}. Message: {message[:200]}")
                continue
            
            # Handle authentication responses
            if "status" in data and "message" in data:
                if _handle_authentication_response(message):
                    is_authenticated = True
                    logger.info("Re-authentication successful")
                continue
            
            # Route messages to appropriate callbacks
            update_type = _identify_update_type(data)
            
            if update_type == UpdateType.ORDER:
                if model.get('order_data'):
                    try:
                        model['order_data'](data)
                        logger.debug("Order callback invoked")
                    except Exception as e:
                        logger.error(f"Error in order callback: {e}", exc_info=True)
            
            elif update_type == UpdateType.POSITION:
                if model.get('position_data'):
                    try:
                        model['position_data'](data)
                        logger.debug("Position callback invoked")
                    except Exception as e:
                        logger.error(f"Error in position callback: {e}", exc_info=True)
            
            elif update_type == UpdateType.OPTION_GREEKS:
                if model.get('subscribe_option_greeks_data'):
                    try:
                        if isinstance(data, dict):
                            for key, value in data.items():
                                if isinstance(value, dict) and "gamma" in value:
                                    model['subscribe_option_greeks_data'](value)
                        logger.debug("Option Greeks callback invoked")
                    except Exception as e:
                        logger.error(f"Error in option Greeks callback: {e}", exc_info=True)
            
            else:  # Market feed
                if model.get('subscribe_feed_data'):
                    try:
                        model['subscribe_feed_data'](data)
                        logger.debug("Feed callback invoked")
                    except Exception as e:
                        logger.error(f"Error in feed callback: {e}", exc_info=True)
        
        except (websocket.WebSocketConnectionClosedException, 
                websocket.WebSocketProtocolException,
                Exception) as e:
            
            # Check if shutdown was requested
            if _is_shutdown_requested(ws):
                logger.info(f"Connection closed intentionally: {type(e).__name__}")
                _clear_shutdown_flag(ws)
                return
            
            # Unexpected disconnection - attempt reconnection
            logger.warning(f"Unexpected disconnection ({type(e).__name__}): {e}")
            print(f"\n⚠ Connection lost: {str(e)[:100]}")
            print("Attempting to reconnect...")
            
            if not connections.check_if_connection_exists(ws):
                logger.info("Connection no longer in manager, stopping reader")
                return
            
            # Attempt reconnection
            new_ws = _attempt_reconnection(
                user_id, ws, config, max_retries, time_interval,
                subscribed_tokens, subscribed_option_greeks_tokens
            )
            
            if new_ws is None:
                logger.error("Failed to reconnect after all attempts")
                print("✗ Failed to reconnect. Please restart the application.")
                return
            
            # Update local reference
            ws = new_ws
            is_authenticated = True
            logger.info("Reconnection successful, resuming message reading")
            
            # Call user's reconnection callback if provided
            if model.get('on_reconnect'):
                try:
                    model['on_reconnect'](new_ws)
                    logger.info("User's on_reconnect callback executed")
                except Exception as callback_error:
                    logger.error(f"Error in on_reconnect callback: {callback_error}", exc_info=True)
            
            continue

def _attempt_reconnection(
    user_id: str,
    old_ws: websocket.WebSocket,
    config: dict,
    max_retries: int,
    time_interval: int,
    subscribed_tokens: List[str],  # This parameter is now unused but kept for compatibility
    subscribed_option_greeks_tokens: List[str]  # This parameter is now unused but kept for compatibility
) -> Optional[websocket.WebSocket]:
    """
    Attempt to reconnect and restore all subscriptions.
    Now uses subscription_tracker for accurate restoration.
    """
    # Get the actual tracked subscriptions (most up-to-date)
    tracked = _get_tracked_subscriptions(old_ws)
    all_tokens = tracked['tokens']
    all_option_greeks_tokens = tracked['option_greeks_tokens']
    
    logger.info(f"Attempting reconnection. Will restore: {len(all_tokens)} market tokens, {len(all_option_greeks_tokens)} option greeks tokens")
    
    for attempt in range(1, max_retries + 1):
        if not connections.check_if_connection_exists(old_ws):
            logger.info("Connection no longer exists in manager, stopping reconnection")
            return None
        
        logger.info(f"Reconnection attempt {attempt}/{max_retries}...")
        print(f"Reconnection attempt {attempt}/{max_retries}...")
        
        time.sleep(time_interval)
        
        try:
            # Create new connection
            base_url, headers, err = get_url_and_header_data(user_id, config)
            if err:
                logger.error(f"Failed to get URL/headers: {err}")
                continue
            
            new_ws = websocket.create_connection(base_url, header=headers)
            logger.info(f"New WebSocket connection created (attempt {attempt})")
            
            # Wait for authentication message
            msg = new_ws.recv()
            logger.info(f"Reconnection auth message: {msg}")
            
            if "Authentication successful" not in msg:
                logger.warning(f"Authentication failed on reconnect: {msg}")
                new_ws.close()
                continue
            
            # Transfer subscription tracking from old connection to new connection
            old_ws_id = id(old_ws)
            new_ws_id = id(new_ws)
            
            # Copy subscription tracker to new connection BEFORE deleting old
            if old_ws_id in subscription_tracker:
                subscription_tracker[new_ws_id] = subscription_tracker[old_ws_id].copy()
                logger.debug(f"Transferred subscription tracking from {old_ws_id} to {new_ws_id}")
            
            # Update connection manager
            connections.delete_connection(old_ws)
            connections.add_connection(new_ws)
            
            logger.info("Connection manager updated with new connection")
            
            # Resubscribe to all tracked tokens
            logger.info("Resubscribing to previous subscriptions...")
            print("Resubscribing to previous feeds...")
            
            # Resubscribe to market feed tokens
            if all_tokens:
                time.sleep(0.5)  # Small delay to ensure connection is stable
                tokens_str = "|".join(all_tokens)
                msg = json.dumps({"action": "subscribe", "tokens": tokens_str})
                
                error = connections.write_message(new_ws, msg.encode())
                if error:
                    logger.error(f"Failed to resubscribe to market tokens: {error}")
                else:
                    logger.info(f"Resubscribed to {len(all_tokens)} market feed token(s): {all_tokens}")
                    print(f"✓ Resubscribed to {len(all_tokens)} market feed token(s)")
            
            if all_option_greeks_tokens:
                time.sleep(0.5)  
                tokens_str = "|".join(all_option_greeks_tokens)
                msg = json.dumps({"action": "subscribe-option-greeks", "tokens": tokens_str})
                
                error = connections.write_message(new_ws, msg.encode())
                if error:
                    logger.error(f"Failed to resubscribe to option Greeks: {error}")
                else:
                    logger.info(f"Resubscribed to {len(all_option_greeks_tokens)} option Greeks token(s): {all_option_greeks_tokens}")
                    print(f"✓ Resubscribed to {len(all_option_greeks_tokens)} option Greeks token(s)")
            
            time.sleep(1)
            
            logger.info("Reconnection and resubscription successful!")
            print("✓ Reconnection complete - all subscriptions restored")
            
            return new_ws
        
        except Exception as e:
            logger.error(f"Reconnection attempt {attempt} failed: {e}", exc_info=True)
            print(f"✗ Attempt {attempt} failed: {str(e)[:100]}...")
            
            if attempt == max_retries:
                logger.error("Max reconnection attempts reached")
                print(f"✗ All {max_retries} reconnection attempts failed")
                return None
    
    return None

def subscribe(ws: websocket.WebSocket, tokens: List[str]) -> Optional[dict]:
    if not connections.check_if_connection_exists(ws):
        return {
            "error": {
                "message": "Connection does not exist"
            }
        }
    
    _track_subscription(ws, tokens, 'tokens')
    
    if len(tokens) == 1 and "|" in tokens[0]:
        tokens_str = tokens[0]
    else:
        tokens_str = "|".join(tokens)
    
    msg = json.dumps({
        "action": "subscribe",
        "tokens": tokens_str
    })
    
    logger.info(f"Sending subscribe message: {msg}")
    error = connections.write_message(ws, msg.encode())
    
    if error:
        return {"error": {"message": error}}
    
    logger.info(f"Subscribe message sent successfully")
    return None

def unsubscribe(ws: websocket.WebSocket, tokens: List[str]) -> Optional[dict]:
    if not connections.check_if_connection_exists(ws):
        return {
            "error": {
                "message": "Connection does not exist"
            }
        }
    
    _untrack_subscription(ws, tokens, 'tokens')
    
    tokens_str = "|".join(tokens)
    msg = json.dumps({
        "action": "unsubscribe",
        "tokens": tokens_str
    })
    
    logger.info(f"Sending unsubscribe message: {msg}")
    error = connections.write_message(ws, msg.encode())
    
    if error:
        return {"error": {"message": error}}
    
    return None

def subscribe_option_greeks(ws: websocket.WebSocket, tokens: List[str]) -> Optional[dict]:
    """Subscribe to option Greeks updates"""
    if not connections.check_if_connection_exists(ws):
        return {
            "error": {
                "message": "Connection does not exist"
            }
        }
    
    _track_subscription(ws, tokens, 'option_greeks_tokens')
    
    if len(tokens) == 1 and "|" in tokens[0]:
        tokens_str = tokens[0]
    else:
        tokens_str = "|".join(tokens)
    
    msg = json.dumps({
        "action": "subscribe-option-greeks",
        "tokens": tokens_str
    })
    
    logger.info(f"Sending subscribe option greeks message: {msg}")
    error = connections.write_message(ws, msg.encode())
    
    if error:
        return {"error": {"message": error}}
    
    logger.info("Subscribe option greeks message sent successfully")
    return None

def unsubscribe_option_greeks(ws: websocket.WebSocket, tokens: List[str]) -> Optional[dict]:
    if not connections.check_if_connection_exists(ws):
        return {
            "error": {
                "message": "Connection does not exist"
            }
        }
    
    _untrack_subscription(ws, tokens, 'option_greeks_tokens')
    
    if len(tokens) == 1 and "|" in tokens[0]:
        tokens_str = tokens[0]
    else:
        tokens_str = "|".join(tokens)
    
    msg = json.dumps({
        "action": "unsubscribe-option-greeks",
        "tokens": tokens_str
    })
    
    logger.info(f"Sending unsubscribe option greeks message: {msg}")
    error = connections.write_message(ws, msg.encode())
    
    if error:
        return {"error": {"message": error}}
    
    logger.info("Unsubscribe option greeks message sent successfully")
    return None
    """Unsubscribe from option Greeks updates"""
    if not connections.check_if_connection_exists(ws):
        return {
            "error": {
                "message": "Connection does not exist"
            }
        }
    
    # Join tokens with pipe delimiter
    if len(tokens) == 1 and "|" in tokens[0]:
        tokens_str = tokens[0]
    else:
        tokens_str = "|".join(tokens)
    
    msg = json.dumps({
        "action": "unsubscribe-option-greeks",
        "tokens": tokens_str
    })
    
    logger.info(f"Sending unsubscribe option greeks message: {msg}")
    error = connections.write_message(ws, msg.encode())
    
    if error:
        return {"error": {"message": error}}
    
    logger.info("Unsubscribe option greeks message sent successfully")
    return None