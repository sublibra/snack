#!/bin/bash

# Development setup script for Snack Chat Service

echo "🍿 Setting up Snack Chat Service development environment..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed. Please install it first:"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo "   or"
    echo "   pip install uv"
    exit 1
fi

echo "✅ uv is installed"

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
    echo "   Snack Chat requires Python >=3.8. If you need a specific version use pyenv or Docker."
    echo "   pyenv example: pyenv install 3.11.14 && pyenv local 3.11.14"
    exit 1
fi

# Create virtual environment and install dependencies with uv
echo "📦 Creating virtual environment and installing dependencies..."
uv venv
uv pip install -e ".[dev]"

# Copy environment file
if [ ! -f ".env" ]; then
    echo "⚙️ Creating .env file..."
    cp .env.example .env
    echo "📝 Please edit .env with your configuration"
else
    echo "✅ .env file already exists"
fi

# Initialize Alembic if no versions exist
if [ ! "$(ls -A alembic/versions)" ]; then
    echo "🗄️ Creating initial database migration..."
    alembic revision --autogenerate -m "Initial migration"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env with your database configuration"
echo "2. Start PostgreSQL database:"
echo "   docker-compose up db -d"
echo "3. Run database migrations:"
echo "   uv run alembic upgrade head"
echo "4. Start the development server:"
echo "   uv run python -m app.main"
echo ""
echo "Or use Docker Compose for everything:"
echo "   docker-compose up"