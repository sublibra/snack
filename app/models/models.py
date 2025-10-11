from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


# Association table for many-to-many relationship between chats and users
chat_members = Table(
    'chat_members',
    Base.metadata,
    Column('chat_id', Integer, ForeignKey('chats.chat_id'), primary_key=True),
    Column('user_id', Integer, ForeignKey('users.user_id'), primary_key=True),
)


class User(Base):
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    public_key = Column(Text, nullable=True)  # For E2EE in Phase 3
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    sent_messages = relationship("Message", back_populates="sender")
    uploaded_media = relationship("Media", back_populates="uploader")
    chats = relationship("Chat", secondary=chat_members, back_populates="members")


class Chat(Base):
    __tablename__ = "chats"
    
    chat_id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    messages = relationship("Message", back_populates="chat")
    members = relationship("User", secondary=chat_members, back_populates="chats")


class Message(Base):
    __tablename__ = "messages"
    
    message_id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("chats.chat_id"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    encrypted_content = Column(Text, nullable=False)  # Encrypted message content
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    chat = relationship("Chat", back_populates="messages")
    sender = relationship("User", back_populates="sent_messages")


class Media(Base):
    __tablename__ = "media"
    
    media_id = Column(Integer, primary_key=True, index=True)
    uploader_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    file_path = Column(String(255), nullable=False)
    encrypted_metadata = Column(Text, nullable=True)  # Encrypted filename, size, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    uploader = relationship("User", back_populates="uploaded_media")