import asyncio
from typing import Dict, Set
from fastapi import WebSocket
from sqlalchemy.orm import Session
from app.models.models import Chat


class ConnectionManager:
    """Manages active WebSocket connections for users."""
    def __init__(self):
        # Store active connections: {user_id: {websocket, ...}}
        self.active_connections: Dict[int, Set[WebSocket]] = {}
        # Store user sessions: {websocket: user_id}
        self.websocket_users: Dict[WebSocket, int] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        """Accept a new WebSocket connection and add it to the tracking dictionaries."""
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)
        self.websocket_users[websocket] = user_id

    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection from tracking."""
        if websocket in self.websocket_users:
            user_id = self.websocket_users[websocket]
            if user_id in self.active_connections:
                self.active_connections[user_id].discard(websocket)
                if not self.active_connections[user_id]:
                    del self.active_connections[user_id]
            del self.websocket_users[websocket]

    async def send_personal_message(self, message: str, user_id: int):
        """Send a message to all connections of a specific user."""
        if user_id in self.active_connections:
            disconnected_websockets = set()
            for websocket in self.active_connections[user_id]:
                try:
                    await websocket.send_text(message)
                except:
                    disconnected_websockets.add(websocket)
            for websocket in disconnected_websockets:
                self.disconnect(websocket)

    async def broadcast_to_chat(
        self,
        message: str,
        chat_id: int,
        db: Session,
        exclude_user_id: int = None
    ):
        """Send a message to all members of a chat."""
        chat = db.query(Chat).filter(Chat.chat_id == chat_id).first()
        if not chat:
            return

        for member in chat.members:
            if exclude_user_id and member.user_id == exclude_user_id:
                continue
            await self.send_personal_message(message, member.user_id)


# Create a singleton instance of the connection manager
manager = ConnectionManager()