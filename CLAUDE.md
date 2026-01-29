# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build & Run Commands

### Backend (Python/FastAPI)
```bash
cd backend
source venv/bin/activate        # Unix (or venv\Scripts\activate on Windows)
pip install -e ".[dev]"         # Install with dev dependencies
uvicorn app.main:app --reload   # Run dev server at localhost:8000
pytest                          # Run all tests
pytest tests/unit/test_task.py  # Run single test file
pytest --cov=app                # Run with coverage
black app/ tests/                # Format code
ruff check app/ tests/           # Lint
```

### Frontend (Next.js/pnpm)
```bash
cd frontend
pnpm install
pnpm dev      # Dev server at localhost:3000
pnpm build    # Production build
pnpm lint     # ESLint
pnpm test     # Vitest
```

## Architecture

This is a **Hexagonal Architecture** (Ports & Adapters) codebase with **Domain-Driven Design**:

```
API Routes (FastAPI)           ← Primary Adapters
        ↓
Application Layer (Use Cases)  ← Orchestration + Port interfaces
        ↓
Domain Layer                   ← Pure business logic, no framework deps
        ↓
Infrastructure                 ← Secondary Adapters (SQLAlchemy, events)
```

### Key Architectural Rules

1. **Domain layer is pure** - `domain/models/` and `domain/services/` have no FastAPI/SQLAlchemy imports
2. **Use Cases orchestrate** - They coordinate domain logic + repositories but contain no business rules
3. **Ports define contracts** - `application/ports/` contains interfaces (UnitOfWork, repositories)
4. **Adapters implement ports** - `infrastructure/persistence/` implements the repository interfaces

### Unit of Work Pattern
All use cases receive a `UnitOfWork` that coordinates transactions across repositories:
```python
with self.uow:
    task = self.uow.tasks.find_by_id(task_id)
    # modify task...
    self.uow.tasks.save(task)
    # commit on exit
```

### Value Objects
Use type-safe wrappers instead of raw UUIDs: `TaskId`, `ProjectId`, `UserId`, `RoleId`, `UtcDateTime` (see `domain/models/value_objects.py`)

### Domain Services vs Use Cases
- **Domain Service** (`domain/services/`): Pure calculation logic, no persistence, easily testable
- **Use Case** (`application/use_cases/`): Orchestrates domain + repositories + events

## Testing Requirements

**Always add tests when adding or changing code:**
- New use case → unit tests in `tests/unit/`
- New domain entity → tests for invariants and key methods
- New API endpoint → use case tests + optional integration tests
- Bug fix → add a regression test first

Test locations:
- `backend/tests/unit/` - Domain and use case tests
- `backend/tests/integration/` - Repository and adapter tests
- `backend/tests/e2e/` - Full API flow tests

## Key Documentation

- `architecture_guide.md` - Hexagonal architecture patterns, SOLID principles, DDD approach
- `Specification_2.1.md` - Business rules (BR-001 to BR-027), use cases, schedule propagation algorithm

## Business Domain

This is a task coordination system with:
- **Tasks** with dependencies forming a DAG
- **Schedule propagation** - delays cascade to dependent tasks (BR-024)
- **Role-based ownership** - tasks assigned to roles, claimed by users with those roles
- **Float-based ranking** - insertion without renumbering (BR-011)
- **Immutable actual dates** - expected dates can change, actual dates are permanent (BR-022)
