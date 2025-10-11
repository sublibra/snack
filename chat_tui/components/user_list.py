"""
User list component for displaying online/offline users
"""

from typing import List, Dict, Any, Optional
from textual.widgets import ListView, ListItem, Label, Input, Static
from textual.containers import Vertical, Horizontal
from textual.reactive import reactive
from textual import events
from rich.text import Text
from datetime import datetime, timedelta


class UserListItem(ListItem):
    """Individual user item in the list"""
    
    def __init__(self, user_data: Dict[str, Any], *args, **kwargs):
        self.user_data = user_data
        super().__init__(*args, **kwargs)
        
    def compose(self):
        username = self.user_data.get("username", "Unknown")
        user_id = self.user_data.get("user_id", 0)
        
        # For now, we'll simulate online/offline status based on recent activity
        # In a real implementation, this would come from the WebSocket or API
        is_online = self._simulate_online_status()
        
        status_color = "green" if is_online else "red"
        status_text = "●" if is_online else "○"
        
        yield Label(
            f"{status_text} {username}",
            classes=f"user_item {'user_online' if is_online else 'user_offline'}"
        )
    
    def _simulate_online_status(self) -> bool:
        """Simulate online status - in real app this would come from API"""
        # Simple hash-based simulation for demo purposes
        return hash(self.user_data.get("username", "")) % 3 != 0


class UserList(Vertical):
    """List of users with search functionality"""
    
    users: reactive[List[Dict[str, Any]]] = reactive([])
    selected_users: reactive[List[Dict[str, Any]]] = reactive([])
    
    def compose(self):
        yield Input(placeholder="Search users...", id="user_search")
        yield Static("Users:", classes="section-header")
        yield ListView(id="users_listview")
    
    async def on_mount(self):
        """Initialize the user list"""
        self.display = True  # Show by default
    
    async def load_users(self, api_client):
        """Load users from the API"""
        try:
            users_data = await api_client.search_users("")
            self.users = users_data
            await self._update_user_list()
        except Exception as e:
            # Handle error - could show in a notification
            pass
    
    async def _update_user_list(self, filter_text: str = ""):
        """Update the displayed user list with optional filtering"""
        listview = self.query_one("#users_listview", ListView)
        listview.clear()
        
        filtered_users = self.users
        if filter_text:
            filtered_users = [
                user for user in self.users 
                if filter_text.lower() in user.get("username", "").lower()
            ]
        
        for user in filtered_users:
            item = UserListItem(user)
            listview.append(item)
    
    async def on_input_changed(self, event: Input.Changed) -> None:
        """Handle search input changes"""
        if event.input.id == "user_search":
            await self._update_user_list(event.value)
    
    async def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle user selection"""
        if event.list_view.id == "users_listview" and event.item:
            user_item = event.item
            if hasattr(user_item, 'user_data'):
                user_data = user_item.user_data
                
                # Toggle selection
                if user_data in self.selected_users:
                    self.selected_users.remove(user_data)
                    user_item.remove_class("selected")
                else:
                    self.selected_users.append(user_data)
                    user_item.add_class("selected")
    
    def get_selected_users(self) -> List[Dict[str, Any]]:
        """Get currently selected users"""
        return self.selected_users.copy()
    
    def clear_selection(self):
        """Clear all user selections"""
        listview = self.query_one("#users_listview", ListView)
        for item in listview.children:
            if hasattr(item, 'remove_class'):
                item.remove_class("selected")
        self.selected_users = []