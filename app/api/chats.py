import asyncio
import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.models import User, Chat, Message
from app.schemas.schemas import (
    ChatCreate, 
    ChatResponse, 
    MessageCreate, 
    MessageResponse
)
from app.core.auth import get_current_user
from app.core.connection_manager import manager

router = APIRouter()


@router.post("/chats", response_model=ChatResponse)
def create_chat(
    chat_data: ChatCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new chat session"""
    # Validate that all user IDs exist
    users = db.query(User).filter(User.user_id.in_(chat_data.user_ids)).all()

    if len(users) != len(chat_data.user_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="One or more user IDs are invalid"
        )
    
    # Add current user to the chat if not already included
    if current_user.user_id not in chat_data.user_ids:
        users.append(current_user)
    
    # Create chat
    chat = Chat()
    db.add(chat)
    db.flush()  # Get the chat_id
    
    # Add members to chat
    chat.members = users
    
    db.commit()
    db.refresh(chat)
    
    return chat


@router.get("/chats", response_model=List[ChatResponse])
def get_user_chats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all chat sessions for the current user"""
    chats = db.query(Chat).join(Chat.members).filter(
        User.user_id == current_user.user_id
    ).all()
    
    return chats


@router.get("/chats/{chat_id}/messages", response_model=List[MessageResponse])
def get_chat_messages(
    chat_id: int,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get message history for a specific chat"""
    # Verify user is a member of the chat
    chat = db.query(Chat).join(Chat.members).filter(
        Chat.chat_id == chat_id,
        User.user_id == current_user.user_id
    ).first()
    
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found or access denied"
        )
    
    # Get messages with pagination
    offset = (page - 1) * limit
    messages = db.query(Message).filter(
        Message.chat_id == chat_id
    ).order_by(
        Message.created_at.desc()
    ).offset(offset).limit(limit).all()
    
    # Reverse to show oldest first
    return list(reversed(messages))


@router.post("/chats/{chat_id}/messages", response_model=MessageResponse)
async def send_message(
    chat_id: int,
    message_data: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a message to a chat and broadcast it to WebSocket clients."""
    # Verify user is a member of the chat
    chat = db.query(Chat).join(Chat.members).filter(
        Chat.chat_id == chat_id,
        User.user_id == current_user.user_id
    ).first()

    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found or access denied"
        )
    
    # Create message
    message = Message(
        chat_id=chat_id,
        sender_id=current_user.user_id,
        encrypted_content=message_data.encrypted_content
    )

    db.add(message)
    db.commit()
    db.refresh(message)
    
    # Prepare message payload for broadcasting
    message_payload = {
        "type": "message",
        "data": {
            "message_id": message.message_id,
            "chat_id": chat_id,
            "sender_id": current_user.user_id,
            "sender_username": current_user.username,
            "encrypted_content": message_data.encrypted_content,
            "created_at": message.created_at.isoformat()
        }
    }

    # Broadcast the message to all members of the chat
    await manager.broadcast_to_chat(
        json.dumps(message_payload),
        chat_id,
        db,
        exclude_user_id=current_user.user_id
    )

    return message