"""
Login screen component
"""

from typing import Optional
from textual.screen import Screen
from textual.widgets import Input, Button, Label, Static
from textual.containers import Vertical, Horizontal, Center
from textual.binding import Binding
from rich.panel import Panel
from rich.text import Text

from ..api_client import SnackAPIClient


class LoginScreen(Screen):
    """Login/Register screen"""
    
    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit"),
        Binding("tab", "toggle_mode", "Register/Login"),
        Binding("enter", "submit", "Submit"),
    ]
    
    CSS = """
    LoginScreen {
        align: center middle;
    }
    
    .login_form {
        width: 50;
        height: 20;
        background: $surface;
        border: solid $primary;
    }
    
    .form_input {
        margin: 1 2;
    }
    
    .form_button {
        margin: 1 2;
    }
    
    .form_label {
        margin: 0 2;
        text-align: center;
    }
    
    .error_message {
        color: $error;
        text-align: center;
        margin: 0 2;
    }
    
    .success_message {
        color: $success;
        text-align: center;
        margin: 0 2;
    }
    """
    
    def __init__(self, api_client: SnackAPIClient, success_callback=None):
        super().__init__()
        self.api_client = api_client
        self.success_callback = success_callback
        self.is_register_mode = False
        
    def compose(self):
        with Center():
            with Vertical(classes="login_form"):
                yield Static("🍿 Snack Chat", classes="form_label")
                yield Static("Login to continue", id="mode_label", classes="form_label")
                yield Input(placeholder="Username", id="username_input", classes="form_input")
                yield Input(
                    placeholder="Password", 
                    password=True, 
                    id="password_input", 
                    classes="form_input"
                )
                yield Button("Login", id="submit_button", variant="primary", classes="form_button")
                yield Button("Switch to Register", id="toggle_button", classes="form_button")
                yield Static("", id="status_message", classes="form_label")
    
    async def on_mount(self):
        """Focus username input on mount"""
        username_input = self.query_one("#username_input", Input)
        username_input.focus()
    
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks"""
        if event.button.id == "submit_button":
            await self.action_submit()
        elif event.button.id == "toggle_button":
            await self.action_toggle_mode()
    
    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key in input fields"""
        await self.action_submit()
    
    async def action_submit(self) -> None:
        """Submit login or register form"""
        username_input = self.query_one("#username_input", Input)
        password_input = self.query_one("#password_input", Input)
        status_message = self.query_one("#status_message", Static)
        
        username = username_input.value.strip()
        password = password_input.value.strip()
        
        if not username or not password:
            status_message.update("Please enter both username and password")
            status_message.add_class("error_message")
            status_message.remove_class("success_message")
            return
        
        try:
            if self.is_register_mode:
                # Register new user
                await self.api_client.register(username, password)
                status_message.update("Registration successful! Please login.")
                status_message.add_class("success_message")
                status_message.remove_class("error_message")
                
                # Switch to login mode
                self.is_register_mode = False
                await self._update_ui_mode()
                
            else:
                # Login existing user
                await self.api_client.login(username, password)
                status_message.update("Login successful!")
                status_message.add_class("success_message")
                status_message.remove_class("error_message")
                
                # Close login screen and return to main app
                if self.success_callback:
                    await self.success_callback()
                self.dismiss()
                
        except Exception as e:
            error_msg = str(e)
            if "400" in error_msg:
                if self.is_register_mode:
                    error_msg = "Username already exists"
                else:
                    error_msg = "Invalid username or password"
            elif "401" in error_msg:
                error_msg = "Invalid username or password"
            else:
                error_msg = f"Error: {error_msg}"
            
            status_message.update(error_msg)
            status_message.add_class("error_message")
            status_message.remove_class("success_message")
    
    async def action_toggle_mode(self) -> None:
        """Toggle between login and register mode"""
        self.is_register_mode = not self.is_register_mode
        await self._update_ui_mode()
        
        # Clear any status messages
        status_message = self.query_one("#status_message", Static)
        status_message.update("")
        status_message.remove_class("error_message")
        status_message.remove_class("success_message")
    
    async def _update_ui_mode(self):
        """Update UI elements based on current mode"""
        mode_label = self.query_one("#mode_label", Static)
        submit_button = self.query_one("#submit_button", Button)
        toggle_button = self.query_one("#toggle_button", Button)
        
        if self.is_register_mode:
            mode_label.update("Register new account")
            submit_button.label = "Register"
            toggle_button.label = "Switch to Login"
        else:
            mode_label.update("Login to continue")
            submit_button.label = "Login"
            toggle_button.label = "Switch to Register"