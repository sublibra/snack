from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Optional


# User schemas
class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    user_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    username: str
    password: str


# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


# Chat schemas
class ChatBase(BaseModel):
    pass


class ChatCreate(BaseModel):
    user_ids: List[int]  # List of user IDs to include in chat


class ChatResponse(ChatBase):
    chat_id: int
    created_at: datetime
    members: List[UserResponse]
    
    model_config = ConfigDict(from_attributes=True)


# Message schemas
class MessageBase(BaseModel):
    encrypted_content: str


class MessageCreate(MessageBase):
    chat_id: int


class MessageResponse(MessageBase):
    message_id: int
    chat_id: int
    sender_id: int
    created_at: datetime
    sender: UserResponse
    
    model_config = ConfigDict(from_attributes=True)


# Media schemas
class MediaBase(BaseModel):
    encrypted_metadata: Optional[str] = None


class MediaResponse(MediaBase):
    media_id: int
    file_path: str
    uploader_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# WebSocket message schemas
class WSMessage(BaseModel):
    type: str  # "message", "typing", "presence", etc.
    data: dict


class WSMessageCreate(BaseModel):
    chat_id: int
    content: str  # This will be encrypted on client side