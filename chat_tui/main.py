"""
Main TUI application built with Textual framework
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
import asyncio

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import (
    Header, Footer, Static, Input, Button, 
    ListView, ListItem, Label, Log, Tabs, Tab
)
from textual.screen import Screen
from textual.binding import Binding
from textual.reactive import reactive
from textual import events
from rich.text import Text
from rich.panel import Panel

from .api_client import SnackAPIClient
from .components.user_list import UserList
from .components.chat_list import ChatList
from .components.message_view import MessageView
from .components.login_screen import LoginScreen


class ChatTUIApp(App):
    """Main chat TUI application"""
    
    CSS = """
    Screen {
        layout: grid;
        grid-size: 3 3;
        grid-gutter: 1;
    }
    
    #sidebar {
        column-span: 1;
        row-span: 3;
        background: $surface;
    }
    
    #main_area {
        column-span: 2;
        row-span: 2;
        background: $background;
    }
    
    #input_area {
        column-span: 2;
        row-span: 1;
        background: $surface;
        height: 3;
    }
    
    Tabs {
        dock: top;
    }
    
    .user_item {
        padding: 0 1;
        margin: 0 0 0 0;
    }
    
    .user_online {
        color: $success;
    }
    
    .user_offline {
        color: $error;
    }
    
    .chat_item {
        padding: 0 1;
        margin: 0 0 1 0;
    }
    
    .message_item {
        padding: 0 1;
        margin: 0 0 1 0;
    }
    
    .my_message {
        text-align: right;
        color: $accent;
    }
    
    .other_message {
        text-align: left;
        color: $text;
    }
    
    Input {
        margin: 0 1;
    }
    
    Button {
        margin: 0 1;
        min-width: 8;
    }
    """
    
    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit"),
        Binding("ctrl+n", "new_chat", "New Chat"),
        Binding("ctrl+u", "toggle_users", "Toggle Users"),
        Binding("ctrl+c", "toggle_chats", "Toggle Chats"),
        Binding("escape", "focus_input", "Focus Input"),
    ]
    
    # Reactive attributes
    current_user = reactive(None)
    selected_chat_id = reactive(None)
    unread_chats = reactive(set())

    def __init__(self):
        super().__init__()
        self.api_client = SnackAPIClient()
        self.current_chat_messages = []
        self.notification_sound = True
        
    def compose(self) -> ComposeResult:
        """Create the main UI layout"""
        yield Header()
        
        # Sidebar with tabs for users and chats
        with Container(id="sidebar"):
            with Tabs():
                yield Tab("Users", id="users_tab")
                yield Tab("Chats", id="chats_tab")
            yield UserList(id="user_list")
            yield ChatList(id="chat_list")
        
        # Main message area
        with Container(id="main_area"):
            yield MessageView(id="message_view")
        
        # Input area for typing messages
        with Horizontal(id="input_area"):
            yield Input(placeholder="Type a message...", id="message_input")
            yield Button("Send", id="send_button", variant="primary")
            yield Button("New Chat", id="new_chat_button", variant="default")
        
        yield Footer()
    
    async def on_mount(self) -> None:
        """Initialize the application"""
        # Check if user is already logged in
        if not await self.api_client.is_authenticated():
            login_screen = LoginScreen(self.api_client, self.on_login_success)
            self.push_screen(login_screen)
        else:
            await self.load_initial_data()
    
    async def on_login_success(self):
        """Callback for successful login"""
        await self.load_initial_data()
    
    async def load_initial_data(self):
        """Load users and chats after authentication"""
        try:
            # Get current user info
            self.current_user = await self.api_client.get_current_user()
            
            # Load users and chats
            user_list = self.query_one("#user_list", UserList)
            chat_list = self.query_one("#chat_list", ChatList) 
            
            await user_list.load_users(self.api_client)
            await chat_list.load_chats(self.api_client)
            # Activate the Chats tab by default so the chat list is visible/selected
            try:
                tabs = self.query_one(Tabs)
                if tabs and tabs.query_one("#chats_tab"):
                    tabs.active = "chats_tab"
            except Exception:
                pass
            
            # Start WebSocket connection for real-time updates
            await self.api_client.start_websocket(self.on_websocket_message)
            
        except Exception as e:
            self.notify(f"Error loading data: {e}", severity="error")
    
    async def on_websocket_message(self, message: Dict[str, Any]):
        """Handle incoming WebSocket messages"""
        try:
            message_type = message.get("type")
            if message_type != "message":
                return

            message_data = message.get("data", {})
            chat_id = message_data.get("chat_id")

            # Mark chat as unread if it's not the currently selected one
            if chat_id and chat_id != self.selected_chat_id:
                self.unread_chats.add(chat_id)
                self.query_one(ChatList).refresh()

            # Show notification for new messages
            if message_data.get("sender_id") != self.current_user.get("user_id"):
                sender = message_data.get("sender_username", "Someone")
                self.notify(f"New message from {sender}")

            # Update message view if it's for the current chat
            if chat_id == self.selected_chat_id:
                message_view = self.query_one("#message_view", MessageView)
                await message_view.add_message(message_data)
                message_view.scroll_to_bottom()

        except Exception as e:
            self.notify(f"Error handling message: {e}", severity="error")
    
    async def on_tabs_tab_activated(self, event: Tabs.TabActivated) -> None:
        """Handle tab switching"""
        user_list = self.query_one("#user_list", UserList)
        chat_list = self.query_one("#chat_list", ChatList)
        
        if event.tab.id == "users_tab":
            user_list.display = True
            chat_list.display = False
        elif event.tab.id == "chats_tab":
            user_list.display = False
            chat_list.display = True
    
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks"""
        if event.button.id == "send_button":
            await self.send_message()
        elif event.button.id == "new_chat_button":
            await self.create_new_chat()
    
    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key in input field"""
        if event.input.id == "message_input":
            await self.send_message()
    
    async def send_message(self):
        """Send a message to the current chat"""
        message_input = self.query_one("#message_input", Input)
        content = message_input.value.strip()
        
        if not content or not self.selected_chat_id:
            return
        
        try:
            # Send message via API
            message = await self.api_client.send_message(
                self.selected_chat_id, content
            )
            
            # Add message to view
            message_view = self.query_one("#message_view", MessageView)
            await message_view.add_message({
                **message,
                "sender_username": self.current_user.get("username")
            })
            
            # Clear input
            message_input.value = ""
            
        except Exception as e:
            self.notify(f"Error sending message: {e}", severity="error")
    
    async def create_new_chat(self):
        """Create a new chat with selected users"""
        user_list = self.query_one("#user_list", UserList)
        selected_users = user_list.get_selected_users()
        
        if not selected_users:
            self.notify("Please select users to chat with", severity="warning")
            return
        
        try:
            user_ids = [user["user_id"] for user in selected_users]
            chat = await self.api_client.create_chat(user_ids)
            
            # Refresh chat list
            chat_list = self.query_one("#chat_list", ChatList)
            await chat_list.load_chats(self.api_client)
            
            # Switch to the new chat
            await self.select_chat(chat["chat_id"])
            
            self.notify("New chat created successfully")
            
        except Exception as e:
            self.notify(f"Error creating chat: {e}", severity="error")
    
    async def select_chat(self, chat_id: int):
        """Select and load a chat, and mark it as read."""
        self.selected_chat_id = chat_id
        
        # Mark chat as read
        if chat_id in self.unread_chats:
            self.unread_chats.remove(chat_id)
            self.query_one(ChatList).refresh()

        try:
            # Load messages for the chat
            messages = await self.api_client.get_chat_messages(chat_id)
            
            # Update message view
            message_view = self.query_one("#message_view", MessageView)
            await message_view.load_messages(messages, chat_id=chat_id)
            message_view.scroll_to_bottom()
            
        except Exception as e:
            self.notify(f"Error loading chat: {e}", severity="error")
    
    async def action_new_chat(self) -> None:
        """Action for Ctrl+N - create new chat"""
        await self.create_new_chat()
    
    async def action_toggle_users(self) -> None:
        """Action for Ctrl+U - show users tab"""
        # Try to activate the users tab if present; otherwise fallback
        tabs = None
        try:
            tabs = self.query_one(Tabs)
        except Exception:
            tabs = None

        if tabs is not None:
            # Ensure the tab exists before activating
            try:
                if tabs.query_one("#users_tab"):
                    tabs.active = "users_tab"
                    return
            except Exception:
                # continue to fallback
                pass

        # Fallback: show/hide the user/chat lists directly
        try:
            user_list = self.query_one("#user_list", UserList)
            chat_list = self.query_one("#chat_list", ChatList)
            user_list.display = True
            chat_list.display = False
        except Exception:
            return
    
    async def action_toggle_chats(self) -> None:
        """Action for Ctrl+C - show chats tab"""
        # Try to activate the chats tab if present; otherwise fallback
        tabs = None
        try:
            tabs = self.query_one(Tabs)
        except Exception:
            tabs = None

        if tabs is not None:
            try:
                if tabs.query_one("#chats_tab"):
                    tabs.active = "chats_tab"
                    return
            except Exception:
                # continue to fallback
                pass

        # Fallback: show/hide the user/chat lists directly
        try:
            user_list = self.query_one("#user_list", UserList)
            chat_list = self.query_one("#chat_list", ChatList)
            user_list.display = False
            chat_list.display = True
        except Exception:
            return
    
    async def action_focus_input(self) -> None:
        """Action for Escape - focus message input"""
        message_input = self.query_one("#message_input", Input)
        message_input.focus()


def run_chat_tui():
    """Entry point for the chat TUI"""
    app = ChatTUIApp()
    app.run()


if __name__ == "__main__":
    run_chat_tui()