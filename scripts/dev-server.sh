#!/bin/bash

# Development server startup script

echo "🍿 Starting Snack Chat Service..."

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Run scripts/setup.sh first"
    exit 1
fi

# Check if uv is available
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed. Please run scripts/setup.sh first"
    exit 1
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
    echo "   Snack Chat requires Python >=3.8. If you need a specific version use pyenv or Docker."
    echo "   pyenv example: pyenv install 3.11.14 && pyenv local 3.11.14"
    exit 1
fi

# Run database migrations
echo "🗄️ Running database migrations..."
VERSIONS_DIR="alembic/versions"
if [ -d "$VERSIONS_DIR" ] && [ -z "$(ls -A $VERSIONS_DIR)" ]; then
    echo "⚠️ No Alembic revisions found in $VERSIONS_DIR — creating tables via SQLAlchemy (dev only)"
    uv run python - <<'PY'
from app.models.models import Base
from app.db.database import engine
print('Creating tables using SQLAlchemy Base.metadata.create_all...')
Base.metadata.create_all(bind=engine)
print('Tables created (if not present).')
PY
else
    if ! uv run alembic upgrade head; then
        echo "⚠️ Alembic migration failed — creating tables via SQLAlchemy (dev only)"
        uv run python - <<'PY'
from app.models.models import Base
from app.db.database import engine
print('Creating tables using SQLAlchemy Base.metadata.create_all...')
Base.metadata.create_all(bind=engine)
print('Tables created (if not present).')
PY
    fi
fi

# Start the server
echo "🚀 Starting FastAPI server..."
uv run python -m app.main