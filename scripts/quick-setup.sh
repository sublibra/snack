#!/bin/bash

# Quick setup script using uv

echo "🍿 Quick setup for Snack Chat Service with uv..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed. Installing now..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    echo "✅ uv installed. Please restart your shell or run: source ~/.bashrc"
    exit 0
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "✅ .env file created. Please edit it with your configuration."
fi

# Install dependencies
echo "📦 Installing dependencies with uv..."
uv venv
uv pip install -e ".[dev]"

echo ""
echo "🎉 Quick setup complete!"
echo ""
echo "To get started:"
echo "1. Edit .env with your database settings (if needed)"
echo "2. Run: make docker-up    (for Docker setup)"
echo "   OR"
echo "   Run: make run          (for local development)"
echo ""
echo "Available make commands:"
echo "  make help              - Show all available commands"
echo "  make run               - Start development server"
echo "  make docker-up         - Start with Docker"
echo "  make test              - Run tests"
echo "  make format            - Format code"