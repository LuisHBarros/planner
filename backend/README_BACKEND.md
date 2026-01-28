# Planner Backend MVP (SQLite sample)

Backend implementation for Planner Multiplayer following Hexagonal Architecture principles.

This `backend/` folder contains a self-contained FastAPI backend configured to use **SQLite** for local development and testing.

## Setup

1. Create a virtual environment:
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # On Windows
# or
source venv/bin/activate  # On Unix
```

2. Install dependencies:
```bash
pip install -e ".[dev]"
```

3. Run the API with SQLite (default):
```bash
uvicorn app.main:app --reload
```

The default database URL is `sqlite:///./planner.db` and the file will be created in the `backend/` directory.

## Project Structure

```
backend/
├── app/
│   ├── api/              # Presentation layer (FastAPI routers, DTOs)
│   ├── application/      # Application layer (use cases, ports)
│   ├── domain/           # Domain layer (entities, value objects, business rules)
│   ├── infrastructure/   # Infrastructure layer (repositories, DB, events, i18n)
│   └── main.py           # Application entry point
└── tests/
    ├── unit/             # Unit tests
    ├── integration/      # Integration tests
    └── e2e/              # End-to-end tests
```

## Testing

Run all tests:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=app --cov-report=html
```

