#!/usr/bin/env python3
"""
Demo script for testing the Chat TUI with mock data

This script is designed to be run with uv:
    uv run chat_tui/demo.py

Or from the repository root:
    uv run -m chat_tui.demo
"""

import asyncio
import sys
import os
from datetime import datetime


# Local import helpers: avoid mutating sys.path at import time
def _ensure_path():
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


_ensure_path()

from chat_tui.main import ChatTUIApp


class MockAPIClient:
    """Mock API client for testing the TUI without a server"""
    
    def __init__(self):
        self.token = "mock_token"
        self.current_user = {
            "user_id": 1,
            "username": "testuser",
            "created_at": datetime.now().isoformat()
        }
        self.mock_users = [
            {"user_id": 2, "username": "alice", "created_at": "2023-01-01T10:00:00Z"},
            {"user_id": 3, "username": "bob", "created_at": "2023-01-01T11:00:00Z"},
            {"user_id": 4, "username": "charlie", "created_at": "2023-01-01T12:00:00Z"},
        ]
        self.mock_chats = [
            {
                "chat_id": 1,
                "created_at": "2023-01-01T14:00:00Z",
                "members": [
                    self.current_user,
                    self.mock_users[0]
                ]
            },
            {
                "chat_id": 2,
                "created_at": "2023-01-01T15:00:00Z",
                "members": [
                    self.current_user,
                    self.mock_users[1],
                    self.mock_users[2]
                ]
            }
        ]
        self.mock_messages = {
            1: [
                {
                    "message_id": 1,
                    "chat_id": 1,
                    "sender_id": 2,
                    "sender_username": "alice",
                    "encrypted_content": "Hey there!",
                    "created_at": "2023-01-01T14:30:00Z"
                },
                {
                    "message_id": 2,
                    "chat_id": 1,
                    "sender_id": 1,
                    "sender_username": "testuser",
                    "encrypted_content": "Hi Alice! How's it going?",
                    "created_at": "2023-01-01T14:31:00Z"
                }
            ],
            2: [
                {
                    "message_id": 3,
                    "chat_id": 2,
                    "sender_id": 3,
                    "sender_username": "bob",
                    "encrypted_content": "Group chat time!",
                    "created_at": "2023-01-01T15:30:00Z"
                }
            ]
        }
    
    async def is_authenticated(self):
        return True
    
    async def get_current_user(self):
        return self.current_user
    
    async def search_users(self, username=""):
        if username:
            return [u for u in self.mock_users if username.lower() in u["username"].lower()]
        return self.mock_users
    
    async def get_chats(self):
        return self.mock_chats
    
    async def create_chat(self, user_ids):
        new_chat = {
            "chat_id": len(self.mock_chats) + 1,
            "created_at": datetime.now().isoformat(),
            "members": [self.current_user] + [u for u in self.mock_users if u["user_id"] in user_ids]
        }
        self.mock_chats.append(new_chat)
        return new_chat
    
    async def get_chat_messages(self, chat_id, page=1, limit=50):
        return self.mock_messages.get(chat_id, [])
    
    async def send_message(self, chat_id, content):
        new_message = {
            "message_id": 100 + len(self.mock_messages.get(chat_id, [])),
            "chat_id": chat_id,
            "sender_id": self.current_user["user_id"],
            "sender_username": self.current_user["username"],
            "encrypted_content": content,
            "created_at": datetime.now().isoformat()
        }
        
        if chat_id not in self.mock_messages:
            self.mock_messages[chat_id] = []
        self.mock_messages[chat_id].append(new_message)
        return new_message
    
    async def start_websocket(self, callback):
        # Mock WebSocket - could simulate some messages
        print("Mock WebSocket connected")
    
    async def close_websocket(self):
        print("Mock WebSocket closed")


class MockChatTUIApp(ChatTUIApp):
    """Chat TUI app with mock API client for testing"""
    
    def __init__(self):
        super().__init__()
        self.api_client = MockAPIClient()


def run_demo():
    """Run the demo TUI with mock data"""
    print("Starting Snack Chat TUI Demo...")
    print("This demo uses mock data and doesn't require a server.")
    print("Press Ctrl+Q to quit.")
    print()
    
    app = MockChatTUIApp()
    app.run()


def main():
    """Main entry point for the demo application."""
    try:
        run_demo()
    except KeyboardInterrupt:
        print("\nDemo ended. Goodbye!")
    except Exception as e:
        print(f"Error running demo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()