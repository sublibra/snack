#!/bin/bash

# Database management script

case "$1" in
    "init")
        echo "🗄️ Initializing database..."
        uv run alembic revision --autogenerate -m "Initial migration"
        ;;
    "migrate")
        message="${2:-Auto migration}"
        echo "🔄 Creating new migration: $message"
        uv run alembic revision --autogenerate -m "$message"
        ;;
    "upgrade")
        echo "⬆️ Upgrading database..."
        uv run alembic upgrade head
        ;;
    "downgrade")
        echo "⬇️ Downgrading database..."
        uv run alembic downgrade -1
        ;;
    "reset")
        echo "🔥 Resetting database (THIS WILL DELETE ALL DATA)..."
        read -p "Are you sure? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            uv run alembic downgrade base
            uv run alembic upgrade head
        else
            echo "Reset cancelled."
        fi
        ;;
    "history")
        echo "📜 Migration history:"
        uv run alembic history --verbose
        ;;
    "current")
        echo "📍 Current migration:"
        uv run alembic current
        ;;
    *)
        echo "Usage: $0 {init|migrate|upgrade|downgrade|reset|history|current}"
        echo ""
        echo "Commands:"
        echo "  init       - Create initial migration"
        echo "  migrate    - Create new migration (optional message)"
        echo "  upgrade    - Apply all pending migrations"
        echo "  downgrade  - Rollback last migration"
        echo "  reset      - Reset database (WARNING: destroys data)"
        echo "  history    - Show migration history"
        echo "  current    - Show current migration"
        exit 1
        ;;
esac