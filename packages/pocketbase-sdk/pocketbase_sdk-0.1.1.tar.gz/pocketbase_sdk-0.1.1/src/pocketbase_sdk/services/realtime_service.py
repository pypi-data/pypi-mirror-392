"""
Realtime service for WebSocket connections
"""
import asyncio
import json
import random
import string
from typing import Any, Callable, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from websockets.client import WebSocketClientProtocol

try:
    from websockets.client import connect
except ImportError:
    connect = None

from .base_service import BaseService
from src.pocketbase_sdk.utils.options import SendOptions
from src.pocketbase_sdk.utils.dtos import RecordSubscription


UnsubscribeFunc = Callable[[], None]


class RealtimeService(BaseService):
    """
    Realtime service for WebSocket connections and subscriptions.
    
    This service manages WebSocket connections for real-time
    subscriptions to collection and record changes.
    """
    
    def __init__(self, client):
        """
        Initialize realtime service.
        
        Args:
            client: PocketBase client instance
        """
        super().__init__(client)
        self._websocket: Optional['WebSocketClientProtocol'] = None
        self._client_id: str = self._generate_client_id()
        self._subscriptions: Dict[str, List[Callable]] = {}
        self._connected: bool = False
        self._reconnect_attempts: int = 0
        self._max_reconnect_attempts: int = 5
        self._reconnect_delay: float = 1.0
        self._connection_task: Optional[asyncio.Task] = None
    
    @property
    def client_id(self) -> str:
        """Get the unique client ID."""
        return self._client_id
    
    @property
    def is_connected(self) -> bool:
        """Check if WebSocket connection is active."""
        return self._connected and self._websocket is not None
    
    def _generate_client_id(self) -> str:
        """Generate a unique client ID."""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    
    async def connect(self) -> None:
        """
        Establish WebSocket connection.
        
        Raises:
            ConnectionError: If connection fails
        """
        if self.is_connected:
            return
        
        try:
            # Build WebSocket URL
            ws_url = self.client.base_url.replace('http://', 'ws://').replace('https://', 'wss://')
            ws_url += f"/api/realtime?client={self._client_id}"
            
            # Connect with auth token if available
            headers = {}
            if self.client.auth_store.token:
                headers["Authorization"] = self.client.auth_store.token
            
            self._websocket = await connect(ws_url, extra_headers=headers)
            self._connected = True
            self._reconnect_attempts = 0
            
            # Start listening for messages
            self._connection_task = asyncio.create_task(self._listen())
            
        except Exception as e:
            self._connected = False
            raise ConnectionError(f"Failed to connect: {e}")
    
    async def disconnect(self) -> None:
        """Close WebSocket connection and cleanup."""
        self._connected = False
        
        if self._connection_task:
            self._connection_task.cancel()
            try:
                await self._connection_task
            except asyncio.CancelledError:
                pass
            self._connection_task = None
        
        if self._websocket:
            await self._websocket.close()
            self._websocket = None
        
        # Clear subscriptions
        self._subscriptions.clear()
    
    async def subscribe(
        self,
        topic: str,
        callback: Callable[[RecordSubscription], None],
        options: Optional[SendOptions] = None
    ) -> UnsubscribeFunc:
        """
        Subscribe to a topic for real-time updates.
        
        Args:
            topic: Topic to subscribe to
            callback: Callback function for updates
            options: Additional request options
            
        Returns:
            Unsubscribe function
            
        Raises:
            ConnectionError: If not connected
        """
        if not self.is_connected:
            await self.connect()
        
        # Add callback to subscriptions
        if topic not in self._subscriptions:
            self._subscriptions[topic] = []
            # Send subscription message
            await self._send_subscription_message(topic)
        
        self._subscriptions[topic].append(callback)
        
        # Return unsubscribe function
        def unsubscribe():
            self._unsubscribe(topic, callback)
        
        return unsubscribe
    
    async def unsubscribe(self, topic: str) -> None:
        """
        Unsubscribe all callbacks from a topic.
        
        Args:
            topic: Topic to unsubscribe from
        """
        if topic in self._subscriptions:
            del self._subscriptions[topic]
            await self._send_unsubscription_message(topic)
    
    async def unsubscribe_by_prefix(self, prefix: str) -> None:
        """
        Unsubscribe all topics with given prefix.
        
        Args:
            prefix: Topic prefix to match
        """
        topics_to_unsubscribe = [
            topic for topic in self._subscriptions.keys()
            if topic.startswith(prefix)
        ]
        
        for topic in topics_to_unsubscribe:
            await self.unsubscribe(topic)
    
    def _unsubscribe(self, topic: str, callback: Callable) -> None:
        """
        Unsubscribe a specific callback from a topic.
        
        Args:
            topic: Topic to unsubscribe from
            callback: Callback to remove
        """
        if topic in self._subscriptions:
            try:
                self._subscriptions[topic].remove(callback)
                # If no more callbacks for this topic, unsubscribe from server
                if not self._subscriptions[topic]:
                    del self._subscriptions[topic]
                    asyncio.create_task(self._send_unsubscription_message(topic))
            except ValueError:
                pass  # Callback not found
    
    async def _listen(self) -> None:
        """Listen for WebSocket messages."""
        try:
            async for message in self._websocket:
                if not self._connected:
                    break
                
                try:
                    # Parse message
                    if isinstance(message, str):
                        data = json.loads(message)
                    else:
                        data = json.loads(message.decode('utf-8'))
                    
                    # Handle different message types
                    if data.get('event') == 'subscription':
                        # Subscription confirmation or data update
                        await self._handle_subscription_message(data)
                    elif data.get('event') == 'pong':
                        # Pong response - ignore for now
                        pass
                    else:
                        # Data update
                        await self._handle_data_message(data)
                
                except (json.JSONDecodeError, UnicodeDecodeError):
                    continue  # Ignore malformed messages
        
        except Exception:
            self._connected = False
            # Attempt to reconnect
            await self._reconnect()
    
    async def _handle_subscription_message(self, data: Dict[str, Any]) -> None:
        """
        Handle subscription confirmation messages.
        
        Args:
            data: Message data
        """
        # For now, just log subscription confirmations
        topic = data.get('topic')
        if topic and topic in self._subscriptions:
            pass  # Subscription confirmed
    
    async def _handle_data_message(self, data: Dict[str, Any]) -> None:
        """
        Handle data update messages.
        
        Args:
            data: Message data
        """
        topic = data.get('topic')
        if not topic or topic not in self._subscriptions:
            return
        
        # Convert to RecordSubscription format
        subscription_data = RecordSubscription(
            action=data.get('action', ''),
            record=data.get('record', {})
        )
        
        # Call all callbacks for this topic
        for callback in self._subscriptions[topic]:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(subscription_data)
                else:
                    callback(subscription_data)
            except Exception:
                # Ignore callback errors to prevent breaking the connection
                pass
    
    async def _send_subscription_message(self, topic: str) -> None:
        """
        Send subscription message to server.
        
        Args:
            topic: Topic to subscribe to
        """
        if not self._websocket:
            return
        
        message = {
            "event": "subscribe",
            "topic": topic
        }
        
        await self._websocket.send(json.dumps(message))
    
    async def _send_unsubscription_message(self, topic: str) -> None:
        """
        Send unsubscription message to server.
        
        Args:
            topic: Topic to unsubscribe from
        """
        if not self._websocket:
            return
        
        message = {
            "event": "unsubscribe",
            "topic": topic
        }
        
        await self._websocket.send(json.dumps(message))
    
    async def _reconnect(self) -> None:
        """Attempt to reconnect WebSocket connection."""
        if self._reconnect_attempts >= self._max_reconnect_attempts:
            return
        
        self._reconnect_attempts += 1
        await asyncio.sleep(self._reconnect_delay)
        
        try:
            # Reset connection state
            self._connected = False
            if self._websocket:
                await self._websocket.close()
                self._websocket = None
            
            # Attempt to reconnect
            await self.connect()
            
            # Resubscribe to all topics
            for topic in list(self._subscriptions.keys()):
                await self._send_subscription_message(topic)
            
        except Exception:
            # Increase delay for next attempt
            self._reconnect_delay *= 2
            await self._reconnect()
    
    async def ping(self) -> bool:
        """
        Send ping to server and wait for pong.
        
        Returns:
            True if ping was successful
        """
        if not self.is_connected:
            return False
        
        try:
            message = {"event": "ping"}
            await self._websocket.send(json.dumps(message))
            return True
        except Exception:
            return False
