"""
HTTP and WebSocket client for the Snack chat API
"""

import asyncio
import json
from typing import Optional, Dict, List, Any, Callable
from datetime import datetime
import httpx
import websockets
from pydantic import BaseModel


class SnackAPIClient:
    """Client for interacting with the Snack chat API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip("/")
        self.token: Optional[str] = None
        self.ws_connection: Optional[websockets.WebSocketClientProtocol] = None
        self.ws_task: Optional[asyncio.Task] = None
        self.message_callback: Optional[Callable] = None
        
    async def is_authenticated(self) -> bool:
        """Check if the client has a valid token"""
        if not self.token:
            return False
            
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/users/me",
                    headers={"Authorization": f"Bearer {self.token}"}
                )
                return response.status_code == 200
        except:
            return False
    
    async def login(self, username: str, password: str) -> Dict[str, Any]:
        """Login and get access token"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/login",
                json={"username": username, "password": password}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data["access_token"]
                return data
            else:
                response.raise_for_status()
    
    async def register(self, username: str, password: str) -> Dict[str, Any]:
        """Register a new user"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/register",
                json={"username": username, "password": password}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                response.raise_for_status()
    
    async def get_current_user(self) -> Dict[str, Any]:
        """Get current user information"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/v1/users/me",
                headers={"Authorization": f"Bearer {self.token}"}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                response.raise_for_status()
    
    async def search_users(self, username: str = "") -> List[Dict[str, Any]]:
        """Search for users by username"""
        async with httpx.AsyncClient() as client:
            params = {"username": username} if username else {}
            response = await client.get(
                f"{self.base_url}/api/v1/users",
                headers={"Authorization": f"Bearer {self.token}"},
                params=params
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                response.raise_for_status()
    
    async def get_chats(self) -> List[Dict[str, Any]]:
        """Get all chats for the current user"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/v1/chats",
                headers={"Authorization": f"Bearer {self.token}"}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                response.raise_for_status()
    
    async def create_chat(self, user_ids: List[int]) -> Dict[str, Any]:
        """Create a new chat with specified users"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/chats",
                headers={"Authorization": f"Bearer {self.token}"},
                json={"user_ids": user_ids}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                response.raise_for_status()
    
    async def get_chat_messages(
        self, 
        chat_id: int, 
        page: int = 1, 
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get messages for a specific chat"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/v1/chats/{chat_id}/messages",
                headers={"Authorization": f"Bearer {self.token}"},
                params={"page": page, "limit": limit}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                response.raise_for_status()
    
    async def send_message(self, chat_id: int, content: str) -> Dict[str, Any]:
        """Send a message to a chat"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/chats/{chat_id}/messages",
                headers={"Authorization": f"Bearer {self.token}"},
                json={"encrypted_content": content}  # For now, using plain text
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                response.raise_for_status()
    
    async def start_websocket(self, message_callback: Callable[[Dict[str, Any]], None]):
        """Start WebSocket connection for real-time updates"""
        if self.ws_connection or not self.token:
            return
        
        self.message_callback = message_callback
        ws_url = f"ws://localhost:8000/ws/chat?token={self.token}"
        
        try:
            self.ws_connection = await websockets.connect(ws_url)
            self.ws_task = asyncio.create_task(self._websocket_handler())
        except Exception as e:
            print(f"WebSocket connection failed: {e}")
    
    async def _websocket_handler(self):
        """Handle incoming WebSocket messages"""
        try:
            while self.ws_connection:
                message = await self.ws_connection.recv()
                data = json.loads(message)
                
                if self.message_callback:
                    await self.message_callback(data)
                    
        except websockets.exceptions.ConnectionClosed:
            print("WebSocket connection closed")
        except Exception as e:
            print(f"WebSocket error: {e}")
    
    async def close_websocket(self):
        """Close WebSocket connection"""
        if self.ws_task:
            self.ws_task.cancel()
            self.ws_task = None
            
        if self.ws_connection:
            await self.ws_connection.close()
            self.ws_connection = None
    
    def logout(self):
        """Logout and clear token"""
        self.token = None
        if self.ws_connection:
            asyncio.create_task(self.close_websocket())


class UserModel(BaseModel):
    """User data model"""
    user_id: int
    username: str
    created_at: datetime


class ChatModel(BaseModel):
    """Chat data model"""
    chat_id: int
    created_at: datetime
    members: List[UserModel]


class MessageModel(BaseModel):
    """Message data model"""
    message_id: int
    chat_id: int
    sender_id: int
    encrypted_content: str
    created_at: datetime