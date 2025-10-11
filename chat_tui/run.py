#!/usr/bin/env python3
"""
Entry point for the Snack Chat TUI application

This script is designed to be run with uv:
    uv run chat_tui/run.py

Or from the repository root:
    uv run -m chat_tui.run
"""

import sys
import os


def main():
    """Main entry point for the chat TUI application."""
    # Add the parent directory to the Python path to ensure imports work
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    # Local import after adjusting sys.path so importing this module doesn't mutate path
    from chat_tui.main import run_chat_tui

    try:
        run_chat_tui()
    except KeyboardInterrupt:
        print("\nGoodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"Error running chat TUI: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()