# Snack Chat Service

A self-hosted chat service with end-to-end encryption built with Python/FastAPI.

## Features

- RESTful API for user management and chat operations
- WebSocket gateway for real-time messaging
- JWT-based authentication
- PostgreSQL database with SQLAlchemy ORM
- End-to-end encryption support (Phase 3)
- File/media sharing (Phase 4)
- Docker deployment ready

## Quick Start

### Option 1: Docker (Recommended)
```bash
docker-compose up -d
```
This will start both the PostgreSQL database and the backend service in a reproducible container environment (recommended for most contributors).

### Option 2: Local dev with uv + binary constraints (works on newer Pythons)
If you prefer to run locally and your host Python is recent (3.9+), use `uv` with the included constraints file which prefers prebuilt binary wheels for compiled extensions.

```bash
# Create a project venv and install editable dev deps using uv (uses pip_constraints.txt)
SKIP_PY_CHECK=1 uv pip install -c pip_constraints.txt -e '.[dev]'
source .venv/bin/activate
cp .env.example .env  # Edit as needed
make run
```

Notes:
- This approach uses `pip_constraints.txt` to prefer prebuilt wheels (pydantic-core, asyncpg, psycopg2-binary, etc.) so you avoid local Rust/C builds on CPython 3.13.
- We require Python >=3.9 for development (see `pyproject.toml`). If you need a project-local interpreter, use `pyenv` (recommended) to install e.g. 3.11.

### Option 3: Traditional pip/venv
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Edit as needed
python -m app.main
```

### make dev vs make dev-unsafe
- `make dev` will run a safe installer that refuses to attempt a local install on unsupported host Pythons.
- `make dev-unsafe` runs the same installer but with `SKIP_PY_CHECK=1`, forcing a local install even if your Python is very new; use it only if you understand the potential for native build failures.

## Development Commands

Using the provided Makefile:

```bash
make help          # Show all available commands
make dev           # Install dev dependencies
make run           # Start development server
make test          # Run tests
make format        # Format code with black and isort
make lint          # Run linting
make docker-up     # Start with Docker Compose
```

## API Documentation

Once running, visit:
- OpenAPI docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Architecture

The service follows a three-tier architecture:
- **API Layer**: FastAPI REST endpoints and WebSocket gateway
- **Business Logic**: Service layer for chat operations
- **Data Layer**: SQLAlchemy models and PostgreSQL database

## Development Phases

This implementation follows the phased approach from the project plan:

- **Phase 1**: Basic WebSocket communication (MVP)
- **Phase 2**: Database persistence and user management  
- **Phase 3**: End-to-end encryption
- **Phase 4**: Media sharing and advanced features
- **Phase 5**: Production deployment and polish

## License

MIT License