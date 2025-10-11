#!/bin/bash
# Installation script for Snack Chat TUI

echo "🍿 Installing Snack Chat TUI..."

# Check if uv is available
if ! command -v uv &> /dev/null; then
    echo "❌ uv is required but not found. Please install uv first."
    echo "Visit: https://github.com/astral-sh/uv#installation"
    exit 1
fi

echo "✅ uv found"

cd "$(dirname "$0")"

# Determine repo root 
REPO_ROOT=$(cd "$(dirname "$0")/.." && pwd)

echo "� Installing Chat TUI dependencies..."

# Go to repo root to use uv properly
cd "$REPO_ROOT"

# Ensure venv exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    uv venv
fi

# Install chat_tui dependencies
echo "Installing chat_tui requirements..."
uv pip install -r chat_tui/requirements.txt

echo "✅ Dependencies installed successfully"

echo ""
echo "🚀 Installation complete!"
echo ""
echo "To run the Chat TUI:"
echo "  uv run chat_tui/run.py          # Connect to real server"
echo "  uv run chat_tui/demo.py         # Run demo with mock data"
echo ""
echo "To start the Snack server (recommended):"
echo "  uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "For more information, see chat_tui/README.md"