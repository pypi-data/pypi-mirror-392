import asyncio
import websockets
import json
from typing import Optional, Callable, Dict, Any
from . import config


class WebSocketClient:
    """WebSocket client for real-time messaging."""
    
    def __init__(self, on_message: Callable[[Dict[str, Any]], None]):
        self.server_url = config.get_server_url()
        self.ws_url = self.server_url.replace("https://", "wss://").replace("http://", "ws://") + "/ws"
        self.on_message = on_message
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.running = False
    
    async def connect(self):
        """Connect to WebSocket server with session cookie."""
        session_token = config.get_session()
        if not session_token:
            raise ValueError("No session token found. Please login first.")
        
        headers = {
            "Cookie": f"connect.sid={session_token}"
        }
        
        try:
            self.websocket = await websockets.connect(self.ws_url, extra_headers=headers)
            self.running = True
        except Exception as e:
            raise ConnectionError(f"Failed to connect to WebSocket: {e}")
    
    async def listen(self):
        """Listen for incoming WebSocket messages."""
        if not self.websocket:
            raise ValueError("Not connected to WebSocket")
        
        try:
            async for message in self.websocket:
                try:
                    data = json.loads(message)
                    self.on_message(data)
                except json.JSONDecodeError:
                    pass
        except websockets.exceptions.ConnectionClosed:
            self.running = False
    
    async def send_message(self, data: Dict[str, Any]):
        """Send message through WebSocket."""
        if not self.websocket:
            raise ValueError("Not connected to WebSocket")
        
        await self.websocket.send(json.dumps(data))
    
    async def close(self):
        """Close WebSocket connection."""
        self.running = False
        if self.websocket:
            await self.websocket.close()
