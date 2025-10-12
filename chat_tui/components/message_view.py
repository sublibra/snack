"""
Message view component for displaying chat messages
"""

from typing import List, Dict, Any, Optional
from textual.widgets import ListView, ListItem, Label, Static
from textual.scroll_view import ScrollView
from textual.containers import Vertical
from textual.reactive import reactive
from textual.scroll_view import ScrollView
from rich.text import Text
from rich.panel import Panel
from datetime import datetime


class MessageItem(ListItem):
    """Individual message item"""
    
    def __init__(self, message_data: Dict[str, Any], current_user_id: int, *args, **kwargs):
        self.message_data = message_data
        self.current_user_id = current_user_id
        super().__init__(*args, **kwargs)
        
    def compose(self):
        sender_id = self.message_data.get("sender_id", 0)
        sender_username = self.message_data.get("sender_username", "Unknown")
        content = self.message_data.get("encrypted_content", "")
        created_at = self.message_data.get("created_at", "")
        
        is_my_message = sender_id == self.current_user_id
        
        # Format timestamp
        try:
            created_dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            time_str = created_dt.strftime("%H:%M")
        except:
            time_str = ""
        
        # Format message display
        if is_my_message:
            display_text = f"{content}  {time_str}"
            classes = "message_item my_message"
        else:
            display_text = f"{sender_username}: {content}  {time_str}"
            classes = "message_item other_message"
        
        yield Label(display_text, classes=classes)


class MessageView(Vertical):
    """View for displaying chat messages"""
    messages: reactive[List[Dict[str, Any]]] = reactive([])
    current_chat_id: reactive[Optional[int]] = reactive(None)
    current_user_id: reactive[Optional[int]] = reactive(None)

    def compose(self):
        yield Static("Select a chat to view messages", id="chat_header")
        yield ScrollView(
            ListView(id="messages_listview"),
            id="messages_scroll"
        )
    
    async def on_mount(self):
        """Initialize the message view"""
        pass
    
    async def load_messages(self, messages: List[Dict[str, Any]], chat_id: Optional[int] = None):
        """Load messages for a chat"""
        if chat_id:
            self.current_chat_id = chat_id
        
        self.messages = messages
        await self._update_message_list()
        
        # Update header
        header = self.query_one("#chat_header", Static)
        if messages:
            # Get chat info from first message or show generic info
            header.update(f"Chat {self.current_chat_id} - {len(messages)} messages")
        else:
            header.update(f"Chat {self.current_chat_id} - No messages yet")
        
        # Scroll to bottom to show latest messages
        self.scroll_to_bottom()
    
    async def add_message(self, message_data: Dict[str, Any]):
        """Add a new message to the view"""
        if not self.current_user_id:
            # Get current user ID from app if not set
            app = self.app
            if hasattr(app, 'current_user') and app.current_user:
                self.current_user_id = app.current_user.get("user_id")
        
        self.messages.append(message_data)
        
        # Add to ListView
        listview = self.query_one("#messages_listview", ListView)
        item = MessageItem(message_data, self.current_user_id or 0)
        listview.append(item)
        
        # Scroll to bottom to show new message
        self.scroll_to_bottom()
    
    async def _update_message_list(self):
        """Update the displayed message list"""
        listview = self.query_one("#messages_listview", ListView)
        listview.clear()
        
        # Get current user ID from app if not set
        if not self.current_user_id:
            app = self.app
            if hasattr(app, 'current_user') and app.current_user:
                self.current_user_id = app.current_user.get("user_id")
        
        # Sort messages by timestamp (oldest first for chat flow)
        sorted_messages = sorted(
            self.messages,
            key=lambda m: m.get("created_at", "")
        )
        
        for message in sorted_messages:
            item = MessageItem(message, self.current_user_id or 0)
            listview.append(item)
    
    def scroll_to_bottom(self):
        """Scroll to the bottom of the message list."""
        try:
            scroll_view = self.query_one("#messages_scroll", ScrollView)
            # Schedule scroll to happen after layout is complete
            self.call_after_refresh(scroll_view.scroll_end, animate=False)
        except Exception:
            # It's okay if this fails (e.g., widget not fully mounted)
            pass
    
    def clear_messages(self):
        """Clear all messages from the view"""
        self.messages = []
        listview = self.query_one("#messages_listview", ListView)
        listview.clear()
        
        header = self.query_one("#chat_header", Static)
        header.update("Select a chat to view messages")