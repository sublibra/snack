# Snack Chat TUI

A modern terminal-based user interface for the Snack chat service built with [Textual](https://textual.textualize.io/).

## Features

- 🔐 **User Authentication** - Login/register with your Snack account
- 👥 **User Discovery** - Search and browse online/offline users
- 💬 **Chat Management** - View your chats and create new conversations
- ⚡ **Real-time Messaging** - Send and receive messages instantly via WebSocket
- 🔔 **Notifications** - Get notified when you receive new messages
- ⌨️ **Keyboard Navigation** - Full keyboard support for efficient navigation

## Screenshots

```
┌─────────────────────────── Snack Chat ────────────────────────────┐
│ Users | Chats                                                      │
├─────────────────┬──────────────────────────────────────────────────┤
│ ● alice         │ alice: Hey there!                    14:32       │
│ ○ bob           │ You: How's it going?                 14:33       │
│ ● charlie       │ alice: Great! Working on the new    14:35       │
│                 │        feature                                   │
│ Search users... │                                                  │
├─────────────────┼──────────────────────────────────────────────────┤
│                 │ Type a message...          [Send] [New Chat]     │
└─────────────────┴──────────────────────────────────────────────────┘
```

## Installation

### Prerequisites

- Python 3.8+
- [uv](https://github.com/astral-sh/uv) - Modern Python package manager
- Access to a running Snack chat server

### Quick Setup

1. **From the repository root:**
   ```bash
   # Install the chat TUI dependencies
   ./chat_tui/install.sh
   ```

   Or manually:
   ```bash
   # Ensure virtual environment exists
   uv venv
   
   # Install chat TUI dependencies
   uv pip install -r chat_tui/requirements.txt
   ```

2. **Run the application:**
   ```bash
   # From repository root
   uv run chat_tui/run.py
   
   # Or run the demo with mock data
   uv run chat_tui/demo.py
   ```

## Usage

### First Time Setup

1. **Start the application** - Run `python run.py`
2. **Create an account** - Press Tab to switch to Register mode, enter username/password
3. **Login** - Switch back to Login mode and enter your credentials

### Navigation

- **Tab/Shift+Tab** - Navigate between UI elements
- **Ctrl+U** - Switch to Users tab
- **Ctrl+C** - Switch to Chats tab  
- **Ctrl+N** - Create new chat with selected users
- **Escape** - Focus message input
- **Enter** - Send message (when in input field)
- **Ctrl+Q** - Quit application

### Creating Chats

1. Switch to the **Users** tab (Ctrl+U)
2. Search for users or browse the list
3. Click on users to select them (multiple selection supported)
4. Press **Ctrl+N** or click **New Chat** button
5. Start chatting!

### Sending Messages

1. Select a chat from the **Chats** tab
2. Type your message in the input field at the bottom
3. Press **Enter** or click **Send**

## Configuration

### Server URL

By default, the TUI connects to `http://localhost:8000`. To change this:

```python
# Edit chat_tui/main.py
self.api_client = SnackAPIClient(base_url="http://your-server:8000")
```

### WebSocket Connection

The WebSocket connection is automatically established at `ws://localhost:8000/ws/chat` when you log in. Make sure your Snack server supports WebSocket connections for real-time features.

## Troubleshooting

### Connection Issues

- **Can't connect to server**: Make sure the Snack server is running and accessible
- **Login fails**: Check your username/password, ensure the server is responding
- **WebSocket errors**: Check server logs, ensure WebSocket endpoint is working

### UI Issues

- **Text not displaying correctly**: Try resizing your terminal or updating to a newer terminal emulator
- **Colors look wrong**: Some terminals may not support all colors, this is normal
- **Keyboard shortcuts not working**: Make sure your terminal forwards key combinations correctly

### Performance Issues

- **Slow startup**: This is normal for the first run, subsequent runs should be faster
- **High CPU usage**: Check for too many WebSocket messages, consider reducing message frequency

## Development

### Project Structure

```
chat_tui/
├── __init__.py          # Package initialization
├── main.py             # Main application and UI layout
├── api_client.py       # HTTP/WebSocket client for Snack API
├── run.py              # Entry point script
├── requirements.txt    # Python dependencies
└── components/         # UI components
    ├── __init__.py
    ├── user_list.py    # User browsing and selection
    ├── chat_list.py    # Chat list display
    ├── message_view.py # Message display and rendering
    └── login_screen.py # Authentication screen
```

### Adding Features

To add new features:

1. **UI Components**: Add new widgets in the `components/` directory
2. **API Calls**: Extend `api_client.py` with new endpoints
3. **Keyboard Shortcuts**: Add bindings in the main app's `BINDINGS` list
4. **Styling**: Update the CSS in `main.py` or component files

### Testing

To test with a local Snack server:

1. **Start the Snack server:**
   ```bash
   # From the repository root
   uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Run the TUI:**
   ```bash
   # Connect to real server
   uv run chat_tui/run.py
   
   # Or run demo with mock data
   uv run chat_tui/demo.py
   ```

3. Create test accounts and try all features

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is part of the Snack chat service. See the main project for license information.