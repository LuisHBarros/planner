# Planner Backend MVP

Backend implementation for Planner Multiplayer following Hexagonal Architecture principles.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -e ".[dev]"
```

3. Set up PostgreSQL database and configure `.env`:
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/planner
ENV=development
```

4. Run migrations (when available):
```bash
alembic upgrade head
```

5. Start the server:
```bash
uvicorn app.main:app --reload
```

## Project Structure

```
app/
├── api/              # Presentation layer (FastAPI routers, DTOs)
├── application/      # Application layer (use cases, ports)
├── domain/           # Domain layer (entities, value objects, business rules)
├── infrastructure/   # Infrastructure layer (repositories, DB, events, i18n)
└── main.py          # Application entry point

tests/
├── unit/            # Unit tests
├── integration/     # Integration tests
└── e2e/             # End-to-end tests
```

## Architecture

This project follows Hexagonal Architecture (Ports and Adapters) with:
- **Domain Layer**: Pure business logic, no framework dependencies
- **Application Layer**: Use cases orchestrate domain logic
- **Infrastructure Layer**: Database, events, external services
- **API Layer**: HTTP endpoints and request/response handling

## Testing

Run all tests:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=app --cov-report=html
```
