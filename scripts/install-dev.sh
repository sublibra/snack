#!/bin/bash

# Install development dependencies with safety checks.

set -euo pipefail

echo "🔧 Installing development dependencies (safe mode)"

# Ensure Python 3 is available
if ! command -v python3 &> /dev/null; then
  echo "❌ python3 not found. Install Python >=3.8 or use Docker."
  exit 1
fi

PY_MAJOR=$(python3 -c 'import sys; print(sys.version_info.major)')
PY_MINOR=$(python3 -c 'import sys; print(sys.version_info.minor)')
PYVER="$PY_MAJOR.$PY_MINOR"

if [ "$PY_MAJOR" -ne 3 ] || [ "$PY_MINOR" -lt 8 ]; then
  echo "❌ Unsupported Python version: $PYVER"
  echo "   Snack Chat requires Python >=3.8 for local dev. Use Docker if you cannot change Python."
  exit 1
fi

# If Python is very new (>=3.13) we warn because some C-extension deps may fail to build.
if [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -ge 13 ]; then
  if [ "${SKIP_PY_CHECK:-0}" = "1" ]; then
    echo "⚠️  Detected Python $PYVER but SKIP_PY_CHECK=1 — attempting install anyway (may fail)"
  else
    echo "⚠️  Detected Python $PYVER. Some dependencies (C extensions) may fail to build on very new Python versions."
    echo "Recommended options:"
    echo "  1) Use Docker: docker-compose up -d" 
    echo "  2) Install a stable local interpreter (pyenv recommended):" 
    echo "     pyenv install 3.11.14 && pyenv local 3.11.14"
    echo "If you still want to attempt local install, re-run with SKIP_PY_CHECK=1 ./scripts/install-dev.sh"
    exit 1
  fi
fi

echo "✅ Python $PYVER looks good — creating venv and installing dev deps..."

if ! command -v uv &> /dev/null; then
  echo "uv not found — installing uv quickly for you"
  curl -LsSf https://astral.sh/uv/install.sh | sh
fi

uv venv
uv pip install -e ".[dev]"

echo "✅ Dev dependencies installed. Activate the venv with: source .venv/bin/activate"
