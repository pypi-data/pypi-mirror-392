import asyncio
import json
from typing import Optional, Callable, Dict, Any
from websockets.asyncio.client import connect as websocket_connect
from websockets.exceptions import ConnectionClosed, InvalidStatusCode
from . import config


class WebSocketClient:
    """WebSocket client for real-time messaging."""
    
    def __init__(self, on_message: Callable[[Dict[str, Any]], None]):
        self.server_url = config.get_server_url()
        self.ws_url = self.server_url.replace("https://", "wss://").replace("http://", "ws://") + "/ws"
        self.on_message = on_message
        self.websocket = None
        self.running = False
    
    async def connect(self):
        """Connect to WebSocket server with session cookie."""
        session_token = config.get_session()
        if not session_token:
            raise ValueError("No session token found. Please login first.")
        
        # Debug: log cookie format (first 30 chars only for security)
        print(f"[DEBUG] Session token starts with: {session_token[:30]}")
        
        headers = {
            "Cookie": f"connect.sid={session_token}"
        }
        
        print(f"[DEBUG] WebSocket URL: {self.ws_url}")
        print(f"[DEBUG] Cookie header: connect.sid={session_token[:30]}...")
        
        try:
            self.websocket = await websocket_connect(self.ws_url, additional_headers=headers)
            self.running = True
            print("[DEBUG] WebSocket connected successfully!")
        except InvalidStatusCode as e:
            print(f"[DEBUG] WebSocket handshake rejected by server:")
            print(f"[DEBUG]   HTTP Status: {e.status_code}")
            if e.headers:
                print(f"[DEBUG]   Response Headers: {dict(e.headers)}")
            # Try to read response body if available
            if e.body:
                try:
                    body_text = e.body.decode('utf-8')
                    print(f"[DEBUG]   Response Body: {body_text}")
                except Exception:
                    print(f"[DEBUG]   Response Body (raw): {e.body[:200]}")
            raise ConnectionError(f"WebSocket authentication failed: Server returned HTTP {e.status_code}. Session may be invalid or expired. Try logging in again.")
        except ConnectionClosed as e:
            print(f"[DEBUG] Connection closed during handshake: code={e.code}, reason={e.reason}")
            raise ConnectionError(f"WebSocket authentication failed (session invalid or expired). Try logging in again.")
        except Exception as e:
            print(f"[DEBUG] Connection error: {type(e).__name__}: {e}")
            raise ConnectionError(f"Failed to connect to WebSocket: {e}")
    
    async def listen(self):
        """Listen for incoming WebSocket messages."""
        if not self.websocket:
            raise ValueError("Not connected to WebSocket")
        
        try:
            async for message in self.websocket:
                # Skip empty messages or control frames
                if not message or not isinstance(message, str):
                    print(f"[DEBUG] Skipping non-text message: type={type(message)}, value={repr(message)[:50]}")
                    continue
                
                # Skip whitespace-only messages
                if not message.strip():
                    print(f"[DEBUG] Skipping empty/whitespace message")
                    continue
                
                try:
                    # Debug: log message type and content
                    print(f"[DEBUG] Received message type: {type(message)}")
                    print(f"[DEBUG] Message content (first 100 chars): {str(message)[:100]}")
                    
                    # Parse JSON
                    data = json.loads(message)
                    self.on_message(data)
                except json.JSONDecodeError as e:
                    print(f"[DEBUG] JSON parsing failed!")
                    print(f"[DEBUG] Error: {e}")
                    print(f"[DEBUG] Message repr: {repr(message)}")
                    print(f"[DEBUG] Message length: {len(message) if message else 0}")
                    print(f"Warning: Received non-JSON message: {message[:100]}")
        except ConnectionClosed as e:
            self.running = False
            if e.code == 1008:  # Policy violation (auth failed)
                raise ConnectionError("WebSocket closed: Authentication failed")
            raise
    
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
