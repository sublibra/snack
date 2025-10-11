"""
Chat list component for displaying user's chats
"""

from typing import List, Dict, Any, Optional
from textual.widgets import ListView, ListItem, Label, Static
from textual.containers import Vertical
from textual.reactive import reactive
from textual import events
from rich.text import Text
from datetime import datetime


class ChatListItem(ListItem):
    """Individual chat item in the list"""
    
    def __init__(self, chat_data: Dict[str, Any], current_user_id: int, *args, **kwargs):
        self.chat_data = chat_data
        self.current_user_id = current_user_id
        super().__init__(*args, **kwargs)
        
    def compose(self):
        chat_id = self.chat_data.get("chat_id", 0)
        members = self.chat_data.get("members", [])
        created_at = self.chat_data.get("created_at", "")
        
        # Get other members (excluding current user)
        other_members = [
            member for member in members 
            if member.get("user_id") != self.current_user_id
        ]
        
        # Create chat display name
        if len(other_members) == 1:
            chat_name = other_members[0].get("username", "Unknown")
        elif len(other_members) > 1:
            names = [member.get("username", "Unknown") for member in other_members[:2]]
            chat_name = ", ".join(names)
            if len(other_members) > 2:
                chat_name += f" +{len(other_members) - 2} more"
        else:
            chat_name = "Empty Chat"
        
        # Format creation time
        try:
            created_dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            time_str = created_dt.strftime("%m/%d %H:%M")
        except:
            time_str = ""
        
        # Create the display text
        display_text = f"💬 {chat_name}"
        if time_str:
            display_text += f"\n   {time_str}"
        
        yield Label(display_text, classes="chat_item")


class ChatList(Vertical):
    """List of user's chats"""
    
    chats: reactive[List[Dict[str, Any]]] = reactive([])
    current_user_id: reactive[Optional[int]] = reactive(None)
    
    def compose(self):
        yield Static("Chats:", classes="section-header")
        yield ListView(id="chats_listview")
    
    async def on_mount(self):
        """Initialize the chat list"""
        self.display = False  # Hidden by default, shown when chats tab is active
    
    async def load_chats(self, api_client):
        """Load chats from the API"""
        try:
            # Get current user info for filtering
            if not self.current_user_id:
                user_info = await api_client.get_current_user()
                self.current_user_id = user_info.get("user_id")
            
            chats_data = await api_client.get_chats()
            self.chats = chats_data
            await self._update_chat_list()
        except Exception as e:
            # Handle error - could show in a notification
            pass
    
    async def _update_chat_list(self):
        """Update the displayed chat list"""
        listview = self.query_one("#chats_listview", ListView)
        listview.clear()
        
        # Sort chats by creation time (newest first)
        sorted_chats = sorted(
            self.chats,
            key=lambda c: c.get("created_at", ""),
            reverse=True
        )
        
        for chat in sorted_chats:
            item = ChatListItem(chat, self.current_user_id or 0)
            listview.append(item)
    
    async def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle chat selection"""
        if event.list_view.id == "chats_listview" and event.item:
            chat_item = event.item
            if hasattr(chat_item, 'chat_data'):
                chat_data = chat_item.chat_data
                chat_id = chat_data.get("chat_id")
                
                # Notify parent app to select this chat
                if chat_id:
                    app = self.app
                    if hasattr(app, 'select_chat'):
                        await app.select_chat(chat_id)
    
    def get_chat_by_id(self, chat_id: int) -> Optional[Dict[str, Any]]:
        """Get chat data by ID"""
        for chat in self.chats:
            if chat.get("chat_id") == chat_id:
                return chat
        return None