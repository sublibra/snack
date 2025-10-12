import json
from typing import Dict, Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.models import User, Chat, Message
from app.core.auth import verify_token
from app.schemas.schemas import WSMessage, WSMessageCreate
from app.core.connection_manager import manager

router = APIRouter()


async def get_websocket_user(
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """Authenticate WebSocket connection using JWT token"""
    try:
        from jose import jwt, JWTError
        from app.core.config import settings
        
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user = db.query(User).filter(User.username == username).first()
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.websocket("/chat")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """WebSocket endpoint for real-time chat"""
    try:
        # Authenticate user
        user = await get_websocket_user(token, db)
        
        # Connect user
        await manager.connect(websocket, user.user_id)
        
        # Send connection confirmation
        await websocket.send_text(json.dumps({
            "type": "connection",
            "data": {
                "status": "connected",
                "user_id": user.user_id,
                "username": user.username
            }
        }))
        
        # Listen for messages
        while True:
            try:
                # Receive message from client
                data = await websocket.receive_text()
                message_data = json.loads(data)
                
                # Handle different message types
                if message_data.get("type") == "message":
                    await handle_chat_message(message_data, user, db)
                elif message_data.get("type") == "typing":
                    await handle_typing_indicator(message_data, user, db)
                elif message_data.get("type") == "presence":
                    await handle_presence_update(message_data, user, db)
                
            except json.JSONDecodeError:
                # Invalid JSON, send error
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "data": {"message": "Invalid JSON format"}
                }))
                
    except HTTPException:
        # Authentication failed, close connection
        await websocket.close(code=1008)  # Policy Violation
        
    except WebSocketDisconnect:
        # Client disconnected
        manager.disconnect(websocket)


async def handle_chat_message(message_data: dict, user: User, db: Session):
    """Handle incoming chat message"""
    try:
        chat_id = message_data["data"]["chat_id"]
        content = message_data["data"]["content"]
        
        # Verify user is member of chat
        chat = db.query(Chat).join(Chat.members).filter(
            Chat.chat_id == chat_id,
            User.user_id == user.user_id
        ).first()
        
        if not chat:
            return  # User not authorized for this chat
        
        # Save message to database
        message = Message(
            chat_id=chat_id,
            sender_id=user.user_id,
            encrypted_content=content  # In Phase 1, this is plain text
        )
        db.add(message)
        db.commit()
        db.refresh(message)
        
        # Broadcast message to all chat members
        message_payload = {
            "type": "message",
            "data": {
                "message_id": message.message_id,
                "chat_id": chat_id,
                "sender_id": user.user_id,
                "sender_username": user.username,
                "content": content,
                "created_at": message.created_at.isoformat()
            }
        }
        
        await manager.broadcast_to_chat(
            json.dumps(message_payload),
            chat_id,
            db,
            exclude_user_id=user.user_id  # Don't send back to sender
        )
        
    except KeyError:
        # Invalid message format
        pass


async def handle_typing_indicator(message_data: dict, user: User, db: Session):
    """Handle typing indicator"""
    try:
        chat_id = message_data["data"]["chat_id"]
        is_typing = message_data["data"]["is_typing"]
        
        # Verify user is member of chat
        chat = db.query(Chat).join(Chat.members).filter(
            Chat.chat_id == chat_id,
            User.user_id == user.user_id
        ).first()
        
        if not chat:
            return
        
        # Broadcast typing indicator to other chat members
        typing_payload = {
            "type": "typing",
            "data": {
                "chat_id": chat_id,
                "user_id": user.user_id,
                "username": user.username,
                "is_typing": is_typing
            }
        }
        
        await manager.broadcast_to_chat(
            json.dumps(typing_payload),
            chat_id,
            db,
            exclude_user_id=user.user_id
        )
        
    except KeyError:
        pass


async def handle_presence_update(message_data: dict, user: User, db: Session):
    """Handle presence/status updates"""
    try:
        status = message_data["data"]["status"]  # online, away, offline
        
        # Broadcast presence to all user's chats
        presence_payload = {
            "type": "presence",
            "data": {
                "user_id": user.user_id,
                "username": user.username,
                "status": status
            }
        }
        
        # Get all chats user is member of
        user_chats = db.query(Chat).join(Chat.members).filter(
            User.user_id == user.user_id
        ).all()
        
        # Broadcast to each chat
        for chat in user_chats:
            await manager.broadcast_to_chat(
                json.dumps(presence_payload),
                chat.chat_id,
                db,
                exclude_user_id=user.user_id
            )
            
    except KeyError:
        pass