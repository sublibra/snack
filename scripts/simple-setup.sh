#!/bin/bash

# Simple uv setup without editable installs

echo "🍿 Setting up Snack Chat Service with uv (simple mode)..."

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
    echo "✅ .env file created."
fi

# Ensure Python version is present and at least 3.8
PYVER=$(python3 -c 'import sys; print("{}.{}".format(sys.version_info.major, sys.version_info.minor))' 2>/dev/null || true)
if [ -z "$PYVER" ]; then
    echo "❌ python3 not found in PATH. Install Python >=3.8 or use Docker."
    exit 1
fi
PY_MAJOR=$(python3 -c 'import sys; print(sys.version_info.major)')
PY_MINOR=$(python3 -c 'import sys; print(sys.version_info.minor)')
if [ "$PY_MAJOR" -ne 3 ] || [ "$PY_MINOR" -lt 8 ]; then
    echo "❌ Unsupported Python version: $PYVER"
    echo "   Snack Chat requires Python >=3.8. If you need an older/newer managed version use pyenv or Docker."
    echo "   pyenv example: pyenv install 3.11.14 && pyenv local 3.11.14"
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
uv venv

# Install core dependencies
echo "🔧 Installing dependencies..."
uv pip install fastapi==0.104.1 \
               uvicorn[standard]==0.24.0 \
               python-multipart==0.0.6 \
               websockets==12.0 \
               sqlalchemy==2.0.23 \
               asyncpg==0.29.0 \
               alembic==1.12.1 \
               "python-jose[cryptography]==3.3.0" \
               "passlib[bcrypt]==1.7.4" \
               pydantic==2.5.0 \
               pydantic-settings==2.1.0

echo "🎉 Setup complete!"
echo ""
echo "To activate the virtual environment:"
echo "  source .venv/bin/activate"
echo ""
echo "To start the development server:"
echo "  uv run python -m app.main"
echo ""
echo "Or use Docker for a cleaner setup:"
echo "  docker-compose up"