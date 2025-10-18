# GitHub Copilot Instructions for Snack Project

## Project Overview
This is a FastAPI-based chat application with real-time messaging capabilities using WebSockets.

## Development Guidelines

### Dependency Management
- **Always use `uv` for dependency management**
  - Install packages: `uv pip install <package>`
  - Run Python scripts: `uv run python <script>`
  - Run the application: `uv run uvicorn app.main:app`
  - Never use `pip` directly

### Code Quality Principles
- **Prefer less code and a clean codebase**
  - Write concise, readable code
  - Remove unnecessary complexity
  - Avoid code duplication - extract reusable functions
  - Use Python idioms and best practices
  - Prefer composition over inheritance
  - Keep functions small and focused on a single responsibility

### Testing & Quality Assurance
- **Always run lint and tests after proposing changes**
  - Preferred linting flow: run `make lint` which uses `uv` to run the project's linters (`uv run ruff check app tests` and `uv run mypy app`). You can also run those commands directly:
    - `uv run ruff check app tests`
    - `uv run mypy app`
  - Run tests: `make test` or `uv run pytest`
  - Fix formatting issues: `make format` (runs `ruff format`). Address `ruff` warnings and `mypy` type issues manually until `make lint` is clean.
  - Ensure all tests pass before considering a change complete

## Project Structure
- `app/` - Main application code
  - `api/` - API endpoints (auth, chats, media, websocket)
  - `core/` - Core functionality (auth, config, connection manager)
  - `db/` - Database configuration
  - `models/` - SQLAlchemy models
  - `schemas/` - Pydantic schemas
  - `services/` - Business logic services
- `tests/` - Test files
- `chat_tui/` - Terminal UI client
- `alembic/` - Database migrations

## Technology Stack
- **Backend**: FastAPI, SQLAlchemy, PostgreSQL
- **Real-time**: WebSockets
- **Authentication**: JWT tokens
- **Testing**: pytest
- **Linting**: ruff
- **Package Management**: uv

## Common Tasks
- Start development server: `make dev` or `uv run uvicorn app.main:app --reload`
- Run tests: `make test`
- Run linting: `make lint` (preferred) or run `uv run ruff check app tests` and `uv run mypy app` directly
- Format code: `make format` (runs `ruff format`)
- Database migrations: `uv run alembic revision --autogenerate -m "description"` then `uv run alembic upgrade head`

## Best Practices
1. Use type hints for all function parameters and return values
2. Write docstrings for complex functions and classes
3. Handle errors gracefully with appropriate HTTP status codes
4. Validate input data using Pydantic schemas
5. Keep database queries in service layer, not in API endpoints
6. Write tests for new features and bug fixes
7. Use async/await for I/O operations
8. Follow RESTful API conventions

## Code Review Checklist
Before proposing changes, ensure:
- [ ] Code follows project structure and conventions
- [ ] All tests pass (`make test`)
- [ ] No linting errors (`make lint`)
- [ ] Type hints are present
- [ ] Error handling is appropriate
- [ ] Code is minimal and clean (no unnecessary complexity)
- [ ] Dependencies added via `uv pip install`
