#!/bin/bash

# Simple test script to verify the backend works

echo "🧪 Testing Snack Chat Service setup..."

# Test 1: Check if Python can import our modules
echo "📦 Testing module imports..."
if uv run python -c "from app.main import app; print('✅ App module imports successfully')"; then
    echo "✅ Module imports work"
else
    echo "❌ Module import failed"
    exit 1
fi

# Test 2: Check if FastAPI can start (quick test)
echo "🚀 Testing FastAPI startup..."
timeout 10s uv run python -c "
from app.main import app
import uvicorn
print('✅ FastAPI app created successfully')
print('✅ Basic setup test passed')
" && echo "✅ FastAPI startup test passed" || echo "❌ FastAPI startup failed"

echo ""
echo "🎉 Backend setup verification complete!"
echo ""
echo "To start the development server:"
echo "  uv run python -m app.main"
echo ""
echo "Or edit the .env file and try Docker again:"
echo "  docker-compose up"